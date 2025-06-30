#include "{{ hpp_file }}"

struct ParseStackValue
{
    uint32_t token;
    uint32_t lineNumber;
    uint32_t indexNumber;
    uint32_t state;
    void* value; // SHOULD NOT OWN THE VALUE
};

static uint32_t tokenize_dfa[{{ tokenizer_num_states }}][95] = {
{%- for row in tokenizer_table %}
	{{ row }}
{%- endfor %}
};

static uint8_t parse_table_action[{{ action_table_shape[0] }}][{{ action_table_shape[1] }}] = {
{%- for row in action_types_table %}
	{{ row }}
{%- endfor %}
};

static uint32_t parse_table_value[{{ action_table_shape[0] }}][{{ action_table_shape[1] }}] = {
{%- for row in action_values_table %}
	{{ row }}
{%- endfor %}
};

{%- for nonterminal, info in resolvable_grammars.items() %}
static {{ info[2][1:-1].strip() }} LexNParseResolve_{{ nonterminal }}(std::stack<ParseStackValue>& parse_stack, uint32_t len, uint32_t id)
{
{%- for rule in info[0] %}
	{%- for symbol in rule %}
		{%- if symbol[1] != '' %}
			{%- if symbol[0] in resolvable_grammars %}
	{{ resolvable_grammars[symbol[0]][2][1:-1].strip() }} {{ symbol[1] }} = nullptr;
			{%- else %}
	std::string {{ symbol[1] }};
			{%- endif %}
		{%- endif %}
	{%- endfor %}
{%- endfor %}

	for (uint32_t i=0;i<len;++i)
	{
		uint32_t symbol_index = len - i - 1;
        void* stack_value = parse_stack.top().value;
        parse_stack.pop();

{%- if info[3][0] > 0 %}
		switch (id)
		{
	{%- for num_var in info[3][1] %}
			case {{ loop.index0 }}:
		{%- if num_var > 0 %}
				goto LexNParse_production{{ loop.index0 }};
		{%- else %}
				continue;
		{%- endif %}
				break;
	{%- endfor %}
			default:
				break;
		}

	{%- for num_var in info[3][1]%}
		{%- if num_var > 0 %}
		LexNParse_production{{ loop.index0 }}:
		switch (symbol_index)
		{
			{%- for symbol in info[0][loop.index0] %}
				{%- if symbol[1] != '' %}
			case {{ loop.index0 }}:
				{%- if symbol[0] in resolvable_grammars %}
				{{ symbol[1] }} = static_cast<{{ resolvable_grammars[symbol[0]][2][1:-1].strip() }}>(stack_value);
				{%- else %}
				{{ symbol[1] }} = *static_cast<std::string*>(stack_value);
				{%- endif %}
				break;
				{%- endif %}
			{%- endfor %}
			default:
				break;
		}
		continue;
		{%- endif %}
	{%- endfor %}
{%- endif %}
	}
	{{ info[1] }}
}
{% endfor %}

{{ resolvable_grammars[start_grammar][2][1:-1].strip() }} LexNParseParse(std::vector<LexNParseToken>& stream)
{
    std::stack<ParseStackValue> parse_stack;
    parse_stack.push({ {{ len(symbols_index) }}, 0, 0, 0, nullptr });
    uint32_t stream_index = 0;

    LexNParseToken terminal_tk = {
        LexNParseTokenType::__terminal__,
        0,
        0,
        "$"
    };

    while (stream_index < stream.size() + 1)
    {
        uint32_t current_state = parse_stack.top().state;
        LexNParseToken& tk = stream_index < stream.size() ? stream[stream_index] : terminal_tk;

        // TODO: error checking if tk is null or terminal and not == end of stream

        uint32_t symbol = static_cast<uint32_t>(tk.type);
        uint8_t action_type = parse_table_action[current_state][symbol];
        uint32_t action_value = parse_table_value[current_state][symbol];

        switch (action_type)
        {
            case 0:
                std::cout << "rejected\n";
                return nullptr;
            case 1:
                parse_stack.push({ symbol, tk.lineNumber, tk.indexNumber, action_value, &tk.token });
                ++ stream_index;
                continue;
			default:
				break;
        }
        // Handle reduce case
        uint32_t nonterminal = 0;
        void* value = nullptr;

		switch(action_value)
		{
	{%- for production in productions %}
			case {{ loop.index0 }}:
		{%- if production.get_nonterminal() == start_grammar %}
				nonterminal = {{ len(symbols_index) }};
		{%- else %}
				nonterminal = {{ symbols_index[production.get_nonterminal()] }};
		{%- endif %}

		{%- if production.get_nonterminal() in resolvable_grammars %}
				value = static_cast<void*>(LexNParseResolve_{{ production.get_nonterminal() }}(parse_stack, {{ len(production.get_symbols()) }}, {{ grammar.lookup_rule_id(production) }}));
		{%- else %}
			{%- if len(production.get_symbols()) > 0 %}
				for (uint32_t i=0;i<{{ len(production.get_symbols()) }};++i)
					parse_stack.pop();
			{%- endif %}
				value = nullptr;
		{%- endif %}
				break;
	{%- endfor %}
			default:
				break;
		}

        // accept state
        if (nonterminal == {{ len(symbols_index) }})
            return static_cast<{{ resolvable_grammars[start_grammar][2][1:-1].strip() }}>(value);

        uint32_t prior_state = parse_stack.top().state;
        uint32_t goto_state = parse_table_value[prior_state][nonterminal];
        // lineNumber, indexNumber, value are arbitrary at the moment
        parse_stack.push({ nonterminal, 0, 0, goto_state, value });
	}

	return nullptr;
}

std::vector<LexNParseToken> LexNParseTokenize(const std::string& input, uint32_t lineNumber)
{

    std::vector<LexNParseToken> tokens;

    uint32_t current_state = 0;
    uint32_t prev_accept_index = 0;
    LexNParseToken prev_accept_token;

    std::string buffer = "";
    uint32_t buffer_begin_index = 0;
    uint32_t current_index = 0;

    while (current_index < input.size())
    {
        char current_input = input[current_index];
        if (current_input < 32 || current_input > 126)
            std::cout << "Invalid input character\n";

        uint32_t input_number = static_cast<uint32_t>(current_input) - 32;
        current_state = tokenize_dfa[current_state][input_number];

        LexNParseTokenType token_type = LexNParseTokenType::__null__;

        switch(current_state)
        {
{%- for accept in accept_states %}
			case {{ accept[0] }}:
				token_type = LexNParseTokenType::{{ accept[1] }};
				break;
{%- endfor %}
            default:
                token_type = LexNParseTokenType::__null__;
        }

        if (current_state == {{ tokenizer_num_states }} || (token_type == LexNParseTokenType::__null__ && current_index == input.size() - 1))
        {
            if (prev_accept_token.type == LexNParseTokenType::__null__)
            {
                std::cout << "Throw invalid token error: line number, column number\n";
                exit(1);
            }

            tokens.push_back(prev_accept_token);

            current_index = prev_accept_index + 1;
            prev_accept_token.type = LexNParseTokenType::__null__;
            buffer = "";
            buffer_begin_index = current_index;
            current_state = 0;
            continue;
        }

        buffer += current_input;
        if (token_type != LexNParseTokenType::__null__)
        {
            // set prev_accept
            prev_accept_token.type = token_type;
            prev_accept_token.lineNumber = lineNumber;
            prev_accept_token.indexNumber = buffer_begin_index;
            prev_accept_token.token = buffer;
            prev_accept_index = current_index;
        }

        ++ current_index;
    }

    if (prev_accept_token.type == LexNParseTokenType::__null__ || prev_accept_index != input.size() - 1)
        std::cout << "throw invalid token error: line number, column number";

    tokens.push_back(prev_accept_token);

    return tokens;
}

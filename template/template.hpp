#include <iostream>
#include <vector>
#include <stack>

{{ header }}

enum class LexNParseTokenType : uint32_t
{
{%- for symbol in symbols %}
	{{ symbol[0] }} = {{ symbol[1] }},
{%- endfor %}
	__null__ = {{ symbols_count }}
};

struct LexNParseToken
{
    LexNParseTokenType type = LexNParseTokenType::__null__;
    uint32_t lineNumber = 0;
    uint32_t indexNumber = 0;
    std::string token = "";
};

{{ start_grammar_dtype }} LexNParseParse(std::vector<LexNParseToken>& stream);
std::vector<LexNParseToken> LexNParseTokenize(const std::string& input, unsigned int lineNumber);


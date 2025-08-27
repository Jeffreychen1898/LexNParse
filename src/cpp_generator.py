from jinja2 import Environment, FileSystemLoader

# really ugly code because jinja code looks convoluted af
# TODO: switch to Mako
class CppGenerator:
    def __init__(self, header, externs, dfa, ambig_priority, grammar_info, parse_table):
        self.header = header
        self.lexer_dfa = dfa
        self.ambig_priority = ambig_priority

        self.externs = externs

        self.start_grammar, self.grammar_info, self.grammar = grammar_info

        self.symbols, self.action_table = parse_table.get_action_table()
        self.productions = parse_table.productions

        self.env = Environment(loader=FileSystemLoader('./'))

    def generate(self, src_hpp, src_cpp, dst_hpp, dst_cpp):
        self.generate_hpp(src_hpp, dst_hpp)
        self.generate_cpp(src_cpp, dst_cpp, dst_hpp)

    def generate_cpp(self, src, dst, hpp_dst):
        template = self.env.get_template(src)

        tokenizer_dfa_as_str = []
        transition_table = self.lexer_dfa.get_transition_table()
        for row in self.lexer_dfa.get_transition_table():
            row_string = ", ".join([str(v) for v in row])
            tokenizer_dfa_as_str.append("{" + row_string + "},")

        dfa_accept_states = self.lexer_dfa.get_accept_states(self.ambig_priority)

        action_type_table = []
        action_value_table = []
        for row in self.action_table:
            action_value_str = ", ".join([str(v[1]) for v in row])
            action_type_row = []
            for action in row:
                if action[0] is None:
                    action_type_row.append("0")
                elif action[0] == "s":
                    action_type_row.append("1")
                elif action[0] == "r":
                    action_type_row.append("2")
                else:
                    action_type_row.append("3")

            action_type_str = ", ".join(action_type_row)

            action_type_table.append("{" + action_type_str + "},")
            action_value_table.append("{" + action_value_str + "},")

        resolvable_grammars = {k: list(v) for k, v in self.grammar_info.items() if len(v[2]) > 0}
        for key in resolvable_grammars:
            total_variables = 0
            variable_counts = []
            for rules in resolvable_grammars[key][0]:
                num_variables = 0
                for tk in rules:
                    if len(tk[1]) > 0:
                        num_variables += 1

                total_variables += num_variables
                variable_counts.append(num_variables)

            resolvable_grammars[key].append((total_variables, variable_counts))

        symbols_index = dict()
        for i, symbol in enumerate(self.symbols):
            symbols_index[symbol[1]] = i

        output = template.render(
            hpp_file=hpp_dst,
            tokenizer_table=tokenizer_dfa_as_str,
            tokenizer_num_states=self.lexer_dfa.get_num_states(),
            accept_states=dfa_accept_states,
            action_types_table=action_type_table,
            action_values_table=action_value_table,
            action_table_shape=(len(self.action_table), len(self.symbols)),
            resolvable_grammars=resolvable_grammars,
            start_grammar=self.start_grammar,
            symbols_index=symbols_index,
            productions=self.productions,
            grammar=self.grammar,
            len=len
        )

        with open(dst, "w") as file:
            file.write(output)

    def generate_hpp(self, src, dst):
        template = self.env.get_template(src)

        dfa_accept_states = self.lexer_dfa.get_accept_states(self.ambig_priority)

        token_symbols = []
        tokens = set([tk[1] for tk in dfa_accept_states])
        tokens.add("__terminal__")

        counter = 0
        for i, tk in enumerate(tokens):
            token_symbols.append((tk, i))
            #token_symbols.append(("__terminal__" if tk == "$" else tk, i))

        start_grammar_dtype = self.grammar_info[self.start_grammar][2][1:-1].strip()

        output = template.render(
            header=self.header,
            externs=self.externs,
            symbols=token_symbols,
            symbols_count=len(token_symbols),
            start_grammar_dtype=start_grammar_dtype,
            len=len
        )

        with open(dst, "w") as file:
            file.write(output)

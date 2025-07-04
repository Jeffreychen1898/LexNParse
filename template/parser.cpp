#include "./template/parser.hpp"

struct ParseStackValue
{
    uint32_t token;
    uint32_t lineNumber;
    uint32_t indexNumber;
    uint32_t state;
    void* value; // SHOULD NOT OWN THE VALUE
};

static uint32_t tokenize_dfa[19][95] = {
	{1, 19, 2, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 5, 19, 6, 19, 19, 19, 19, 19, 19, 19, 19, 7, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 8, 19, 19, 19, 19, 19, 19, 9, 19, 10, 19},
	{1, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{2, 2, 18, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 16, 19, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 14, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 11, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 12, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 13, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 15, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 12, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},
	{2, 2, 18, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2},
};

static uint8_t parse_table_action[23][16] = {
	{0, 3, 0, 3, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0},
	{2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
	{2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
	{0, 0, 3, 0, 0, 0, 0, 2, 2, 2, 0, 2, 0, 2, 2, 2},
	{0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 2},
	{0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 2, 0, 1, 2},
	{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1},
	{0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 2},
	{0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0},
	{2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2},
	{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0},
	{0, 0, 0, 0, 0, 3, 0, 0, 2, 2, 0, 2, 0, 2, 1, 2},
	{0, 3, 0, 3, 0, 0, 3, 0, 1, 1, 0, 1, 0, 1, 0, 1},
	{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 2},
	{0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2},
	{0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2},
	{0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2},
	{0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2},
	{0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2},
	{0, 0, 0, 0, 0, 3, 0, 2, 2, 2, 0, 2, 0, 2, 1, 2},
	{0, 3, 0, 3, 0, 0, 3, 1, 1, 1, 0, 1, 0, 1, 0, 1},
	{0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 0, 2, 2, 2},
	{2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2},
};

static uint32_t parse_table_value[23][16] = {
	{0, 2, 0, 1, 0, 0, 0, 0, 3, 0, 0, 0, 0, 4, 0, 0},
	{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
	{1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
	{0, 0, 19, 0, 0, 0, 0, 2, 2, 2, 0, 2, 0, 2, 2, 2},
	{0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 3, 0, 3, 3},
	{0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 4, 0, 7, 4},
	{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 8},
	{0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 5},
	{0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 4, 0, 0, 0, 7, 0},
	{6, 0, 0, 0, 0, 0, 0, 6, 6, 6, 0, 6, 6, 6, 6, 6},
	{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 0, 0, 0, 0, 0},
	{0, 0, 0, 0, 0, 12, 0, 0, 4, 4, 0, 4, 0, 4, 7, 4},
	{0, 17, 0, 16, 0, 0, 13, 0, 3, 18, 0, 14, 0, 4, 0, 15},
	{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 7},
	{0, 0, 0, 0, 0, 0, 0, 8, 8, 8, 0, 8, 8, 8, 8, 8},
	{0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 0, 9, 9, 9, 9, 9},
	{0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 0, 10, 10, 10, 10, 10},
	{0, 0, 0, 0, 0, 0, 0, 11, 11, 11, 0, 11, 11, 11, 11, 11},
	{0, 0, 0, 0, 0, 0, 0, 12, 12, 12, 0, 12, 12, 12, 12, 12},
	{0, 0, 0, 0, 0, 20, 0, 4, 4, 4, 0, 4, 0, 4, 7, 4},
	{0, 17, 0, 16, 0, 0, 21, 22, 3, 18, 0, 14, 0, 4, 0, 15},
	{0, 0, 0, 0, 0, 0, 0, 13, 13, 13, 0, 13, 0, 13, 13, 13},
	{14, 0, 0, 0, 0, 0, 0, 14, 14, 14, 0, 14, 14, 14, 14, 14},
};
static ASTJsonNode* LexNParseResolve_JSON(std::stack<ParseStackValue>& parse_stack, uint32_t len, uint32_t id)
{
	ASTArrayNode* arr = nullptr;
	ASTObjectNode* obj = nullptr;

	for (uint32_t i=0;i<len;++i)
	{
		uint32_t symbol_index = len - i - 1;
        void* stack_value = parse_stack.top().value;
        parse_stack.pop();
		switch (id)
		{
			case 0:
				goto LexNParse_production0;
				break;
			case 1:
				goto LexNParse_production1;
				break;
			default:
				break;
		}
		LexNParse_production0:
		switch (symbol_index)
		{
			case 0:
				arr = static_cast<ASTArrayNode*>(stack_value);
				break;
			default:
				break;
		}
		continue;
		LexNParse_production1:
		switch (symbol_index)
		{
			case 0:
				obj = static_cast<ASTObjectNode*>(stack_value);
				break;
			default:
				break;
		}
		continue;
	}
	
    ASTJsonNode* new_node = new ASTJsonNode();
    new_node->type = ASTValueType::Json;
    if (id == 0)
        new_node->array = arr;
    else
        new_node->object = obj;

    return new_node;

}

static ASTArrayNode* LexNParseResolve_ARRAY(std::stack<ParseStackValue>& parse_stack, uint32_t len, uint32_t id)
{
	std::vector<ASTValueNode*>* val = nullptr;

	for (uint32_t i=0;i<len;++i)
	{
		uint32_t symbol_index = len - i - 1;
        void* stack_value = parse_stack.top().value;
        parse_stack.pop();
		switch (id)
		{
			case 0:
				goto LexNParse_production0;
				break;
			default:
				break;
		}
		LexNParse_production0:
		switch (symbol_index)
		{
			case 1:
				val = static_cast<std::vector<ASTValueNode*>*>(stack_value);
				break;
			default:
				break;
		}
		continue;
	}
	
    ASTArrayNode* new_node = new ASTArrayNode();
    new_node->type = ASTValueType::Array;
    new_node->values = val;

    return new_node;

}

static ASTObjectNode* LexNParseResolve_OBJECT(std::stack<ParseStackValue>& parse_stack, uint32_t len, uint32_t id)
{
	std::unordered_map<std::string, ASTValueNode*>* val = nullptr;

	for (uint32_t i=0;i<len;++i)
	{
		uint32_t symbol_index = len - i - 1;
        void* stack_value = parse_stack.top().value;
        parse_stack.pop();
		switch (id)
		{
			case 0:
				goto LexNParse_production0;
				break;
			default:
				break;
		}
		LexNParse_production0:
		switch (symbol_index)
		{
			case 1:
				val = static_cast<std::unordered_map<std::string, ASTValueNode*>*>(stack_value);
				break;
			default:
				break;
		}
		continue;
	}
	
    ASTObjectNode* new_node = new ASTObjectNode();
    new_node->type = ASTValueType::Object;
    new_node->values = val;

    return new_node;

}

static std::unordered_map<std::string, ASTValueNode*>* LexNParseResolve_OBJECT_VALUE(std::stack<ParseStackValue>& parse_stack, uint32_t len, uint32_t id)
{
	std::unordered_map<std::string, ASTValueNode*>* prev = nullptr;
	std::string key;
	ASTValueNode* value = nullptr;

	for (uint32_t i=0;i<len;++i)
	{
		uint32_t symbol_index = len - i - 1;
        void* stack_value = parse_stack.top().value;
        parse_stack.pop();
		switch (id)
		{
			case 0:
				goto LexNParse_production0;
				break;
			case 1:
				continue;
				break;
			default:
				break;
		}
		LexNParse_production0:
		switch (symbol_index)
		{
			case 0:
				prev = static_cast<std::unordered_map<std::string, ASTValueNode*>*>(stack_value);
				break;
			case 2:
				key = *static_cast<std::string*>(stack_value);
				break;
			case 6:
				value = static_cast<ASTValueNode*>(stack_value);
				break;
			default:
				break;
		}
		continue;
	}
	
    if (id == 1)
    {
        std::unordered_map<std::string, ASTValueNode*>* new_node = new std::unordered_map<std::string, ASTValueNode*>();
        return new_node;
    }

    prev->insert({ key, value });

    return prev;

}

static std::vector<ASTValueNode*>* LexNParseResolve_ARRAY_VALUE(std::stack<ParseStackValue>& parse_stack, uint32_t len, uint32_t id)
{
	std::vector<ASTValueNode*>* prev = nullptr;
	ASTValueNode* value = nullptr;

	for (uint32_t i=0;i<len;++i)
	{
		uint32_t symbol_index = len - i - 1;
        void* stack_value = parse_stack.top().value;
        parse_stack.pop();
		switch (id)
		{
			case 0:
				goto LexNParse_production0;
				break;
			case 1:
				continue;
				break;
			default:
				break;
		}
		LexNParse_production0:
		switch (symbol_index)
		{
			case 0:
				prev = static_cast<std::vector<ASTValueNode*>*>(stack_value);
				break;
			case 2:
				value = static_cast<ASTValueNode*>(stack_value);
				break;
			default:
				break;
		}
		continue;
	}
	
    if (id == 1)
        return new std::vector<ASTValueNode*>();

    prev->push_back(value);

    return prev;

}

static ASTValueNode* LexNParseResolve_VALUE(std::stack<ParseStackValue>& parse_stack, uint32_t len, uint32_t id)
{
	ASTArrayNode* arr = nullptr;
	ASTObjectNode* obj = nullptr;
	std::string boolean;
	std::string number;
	std::string string;

	for (uint32_t i=0;i<len;++i)
	{
		uint32_t symbol_index = len - i - 1;
        void* stack_value = parse_stack.top().value;
        parse_stack.pop();
		switch (id)
		{
			case 0:
				goto LexNParse_production0;
				break;
			case 1:
				goto LexNParse_production1;
				break;
			case 2:
				goto LexNParse_production2;
				break;
			case 3:
				goto LexNParse_production3;
				break;
			case 4:
				goto LexNParse_production4;
				break;
			default:
				break;
		}
		LexNParse_production0:
		switch (symbol_index)
		{
			case 0:
				arr = static_cast<ASTArrayNode*>(stack_value);
				break;
			default:
				break;
		}
		continue;
		LexNParse_production1:
		switch (symbol_index)
		{
			case 0:
				obj = static_cast<ASTObjectNode*>(stack_value);
				break;
			default:
				break;
		}
		continue;
		LexNParse_production2:
		switch (symbol_index)
		{
			case 0:
				boolean = *static_cast<std::string*>(stack_value);
				break;
			default:
				break;
		}
		continue;
		LexNParse_production3:
		switch (symbol_index)
		{
			case 0:
				number = *static_cast<std::string*>(stack_value);
				break;
			default:
				break;
		}
		continue;
		LexNParse_production4:
		switch (symbol_index)
		{
			case 0:
				string = *static_cast<std::string*>(stack_value);
				break;
			default:
				break;
		}
		continue;
	}
	
    switch (id)
    {
        case 0:
            return arr;
            break;
        case 1:
            return obj;
            break;
    }
    ASTPrimNode* new_node = new ASTPrimNode();
    new_node->type = ASTValueType::Prim;
    switch (id)
    {
        case 2:
            new_node->prim = boolean;
            break;
        case 3:
            new_node->prim = number;
            break;
        case 4:
            new_node->prim = string;
            break;
    }

    return new_node;

}


ASTJsonNode* LexNParseParse(std::vector<LexNParseToken>& stream)
{
    std::stack<ParseStackValue> parse_stack;
    parse_stack.push({ 16, 0, 0, 0, nullptr });
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
			case 0:
				nonterminal = 16;
				value = static_cast<void*>(LexNParseResolve_JSON(parse_stack, 1, 1));
				break;
			case 1:
				nonterminal = 16;
				value = static_cast<void*>(LexNParseResolve_JSON(parse_stack, 1, 0));
				break;
			case 2:
				nonterminal = 2;
				value = static_cast<void*>(LexNParseResolve_ARRAY_VALUE(parse_stack, 0, 1));
				break;
			case 3:
				nonterminal = 4;
				value = static_cast<void*>(LexNParseResolve_OBJECT_VALUE(parse_stack, 0, 1));
				break;
			case 4:
				nonterminal = 5;
				value = nullptr;
				break;
			case 5:
				nonterminal = 5;
				for (uint32_t i=0;i<1;++i)
					parse_stack.pop();
				value = nullptr;
				break;
			case 6:
				nonterminal = 3;
				value = static_cast<void*>(LexNParseResolve_OBJECT(parse_stack, 4, 0));
				break;
			case 7:
				nonterminal = 4;
				value = static_cast<void*>(LexNParseResolve_OBJECT_VALUE(parse_stack, 7, 0));
				break;
			case 8:
				nonterminal = 6;
				value = static_cast<void*>(LexNParseResolve_VALUE(parse_stack, 1, 3));
				break;
			case 9:
				nonterminal = 6;
				value = static_cast<void*>(LexNParseResolve_VALUE(parse_stack, 1, 4));
				break;
			case 10:
				nonterminal = 6;
				value = static_cast<void*>(LexNParseResolve_VALUE(parse_stack, 1, 1));
				break;
			case 11:
				nonterminal = 6;
				value = static_cast<void*>(LexNParseResolve_VALUE(parse_stack, 1, 0));
				break;
			case 12:
				nonterminal = 6;
				value = static_cast<void*>(LexNParseResolve_VALUE(parse_stack, 1, 2));
				break;
			case 13:
				nonterminal = 2;
				value = static_cast<void*>(LexNParseResolve_ARRAY_VALUE(parse_stack, 3, 0));
				break;
			case 14:
				nonterminal = 1;
				value = static_cast<void*>(LexNParseResolve_ARRAY(parse_stack, 4, 0));
				break;
			default:
				break;
		}

        // accept state
        if (nonterminal == 16)
            return static_cast<ASTJsonNode*>(value);

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
			case 1:
				token_type = LexNParseTokenType::space;
				break;
			case 3:
				token_type = LexNParseTokenType::number;
				break;
			case 4:
				token_type = LexNParseTokenType::colon;
				break;
			case 5:
				token_type = LexNParseTokenType::arr_open;
				break;
			case 6:
				token_type = LexNParseTokenType::arr_close;
				break;
			case 9:
				token_type = LexNParseTokenType::obj_open;
				break;
			case 10:
				token_type = LexNParseTokenType::obj_close;
				break;
			case 13:
				token_type = LexNParseTokenType::boolean;
				break;
			case 17:
				token_type = LexNParseTokenType::number;
				break;
			case 18:
				token_type = LexNParseTokenType::string;
				break;
            default:
                token_type = LexNParseTokenType::__null__;
        }

        if (current_state == 19 || (token_type == LexNParseTokenType::__null__ && current_index == input.size() - 1))
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
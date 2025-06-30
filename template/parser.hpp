#include <iostream>
#include <vector>
#include <stack>


#include "ast.hpp"


enum class LexNParseTokenType : uint32_t
{
	__terminal__ = 0,
	arr_close = 7,
	arr_open = 8,
	boolean = 9,
	colon = 10,
	number = 11,
	obj_close = 12,
	obj_open = 13,
	space = 14,
	string = 15,
	__null__ = 16
};

struct LexNParseToken
{
    LexNParseTokenType type = LexNParseTokenType::__null__;
    uint32_t lineNumber = 0;
    uint32_t indexNumber = 0;
    std::string token = "";
};

ASTJsonNode* LexNParseParse(std::vector<LexNParseToken>& stream);
std::vector<LexNParseToken> LexNParseTokenize(const std::string& input, unsigned int lineNumber);

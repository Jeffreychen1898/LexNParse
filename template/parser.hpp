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
	endline = 17,
	__null__ = 16
};

enum class LexNParseErrorCode : uint8_t
{
	None,
	InvalidCharacter,
	InvalidToken,
	IncompleteParse,
	InvalidParse
};

struct LexNParseToken
{
    LexNParseTokenType type = LexNParseTokenType::__null__;
    uint32_t lineNumber = 0;
    uint32_t indexNumber = 0;
    std::string token = "";
};

struct LexNParseStatus
{
	bool complete = false;
	LexNParseErrorCode errorCode;
	uint32_t lineNumber;
	uint32_t indexNumber;
};

struct LexNParseResult
{
	LexNParseStatus status;
	ASTJsonNode* value;
};

LexNParseResult LexNParseParse(std::vector<LexNParseToken>& stream);
LexNParseStatus LexNParseTokenize(std::vector<LexNParseToken>& tokens, const std::string& input, unsigned int lineNumber);
#include <iostream>
#include <vector>
#include <stack>

{{ header }}

enum class LexNParseTokenType : uint32_t
{
{%- for symbol in symbols %}
	{{ symbol[0] }} = {{ symbol[1] }},
{%- endfor %}
{%- for extern in externs %}
	{{ extern }} = {{ symbols_count + loop.index0 + 1 }},
{%- endfor %}
	__null__ = {{ symbols_count }}
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
	{{ start_grammar_dtype }} value;
};

LexNParseResult LexNParseParse(std::vector<LexNParseToken>& stream);
LexNParseStatus LexNParseTokenize(std::vector<LexNParseToken>& tokens, const std::string& input, unsigned int lineNumber);

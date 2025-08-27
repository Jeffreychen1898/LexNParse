#include <iostream>

#include "./parser.hpp"

static std::string stringify(LexNParseToken tk)
{
    std::string type;
    switch(tk.type)
    {
        case LexNParseTokenType::space:
            type = "space";
            break;
        case LexNParseTokenType::colon:
            type = "colon";
            break;
        case LexNParseTokenType::arr_open:
            type = "array_open";
            break;
        case LexNParseTokenType::arr_close:
            type = "array_close";
            break;
        case LexNParseTokenType::obj_open:
            type = "object_open";
            break;
        case LexNParseTokenType::obj_close:
            type = "object_close";
            break;
        case LexNParseTokenType::boolean:
            type = "boolean";
            break;
        case LexNParseTokenType::number:
            type = "number";
            break;
        case LexNParseTokenType::string:
            type = "string";
            break;
        case LexNParseTokenType::__null__:
            type = "NULL";
            break;
        default:
            break;
    }
    /*std::string location(tk.line_number);
    location += ":";
    location += std::string(tk.index_number);*/

    return std::to_string(tk.lineNumber) + ":" + std::to_string(tk.indexNumber) + " " + type + " : " + tk.token;
}

std::string testcode[16] = {
    "{\"mynum\" : 5",
    "    \"mybool\": true",
    "    \"mystr\":  false",
    "    \"myarr\": [",
    "        5 7 9 2",
    "    ]",
    "    \"myobj\": {",
    "        \"objs\": [",
    "            { \"hello\":",
    "                        \"world\"",
    "              \"foo\":",
    "                   \"bar\"",
    "            }",
    "        ]",
    "    }",
    "}"
};
/*std::string testcode[3] = {
    "{ ",
    "  \"asdf\": 6",
    "}"
};*/

void printValueNode(ASTValueNode* val, uint32_t tabs);
void printArrNode(ASTArrayNode* arr, uint32_t tabs);
void printObjNode(ASTObjectNode* obj, uint32_t tabs);
void printPrimNode(ASTPrimNode* prim, uint32_t tabs);

void printValueNode(ASTValueNode* val, uint32_t tabs)
{
    switch (val->type)
    {
        case ASTValueType::Array:
            printArrNode(static_cast<ASTArrayNode*>(val), tabs);
            break;
        case ASTValueType::Object:
            printObjNode(static_cast<ASTObjectNode*>(val), tabs);
            break;
        case ASTValueType::Prim:
            printPrimNode(static_cast<ASTPrimNode*>(val), tabs);
            break;
        default:
            break;
    }
}

void printArrNode(ASTArrayNode* arr, uint32_t tabs)
{
    for (int i=0;i<tabs;++i)
        std::cout << "\t";
    std::cout << "[\n";

    for (int i=0;i<arr->values->size();++i)
    {
        printValueNode(arr->values->at(i), tabs + 1);
    }

    for (int i=0;i<tabs;++i)
        std::cout << "\t";
    std::cout << "]\n";
}

void printObjNode(ASTObjectNode* obj, uint32_t tabs)
{
    for (int i=0;i<tabs;++i)
        std::cout << "\t";
    std::cout << "{\n";

    for (auto it=obj->values->begin();it != obj->values->end();++it)
    {
        for (int i=0;i<tabs + 1;++i)
            std::cout << "\t";
        std::cout << it->first << "\n";

        printValueNode(it->second, tabs + 1);
        std::cout << "\n";
    }

    for (int i=0;i<tabs;++i)
        std::cout << "\t";
    std::cout << "}\n";
}

void printPrimNode(ASTPrimNode* prim, uint32_t tabs)
{
    for (int i=0;i<tabs;++i)
        std::cout << "\t";
    std::cout << prim->prim << "\n";
}

int main()
{
    // requires preprocessing to ensure all tokens are displayable ascii [32-126]
    std::vector<LexNParseToken> total_tk;
    for (int i=0;i<16;++i)
    {
        std::vector<LexNParseToken> v;
        LexNParseStatus status = LexNParseTokenize(v, testcode[i], i);
        if (!status.complete)
        {
            std::cout << static_cast<int>(status.errorCode) << "\n";
            std::cout << status.lineNumber << "\n";
            std::cout << status.indexNumber << "\n";
            exit(1);
        }
        total_tk.insert(total_tk.end(), v.begin(), v.end());
        for (auto tk : v)
        {
            std::cout << stringify(tk) << "\n";
        }
    }

	std::cout << "\n\n";

    LexNParseResult result = LexNParseParse(total_tk);
    if (!result.status.complete)
    {
        std::cout << static_cast<int>(result.status.errorCode) << "\n";
        std::cout << result.status.lineNumber << "\n";
        std::cout << result.status.indexNumber << "\n";
        exit(1);
    }
    printObjNode(result.value->object, 0);

    return 0;
}

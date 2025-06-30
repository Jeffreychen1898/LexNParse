#include <vector>
#include <unordered_map>

enum class ASTValueType
{
    Array, Object, Prim, Json, None
};

struct ASTValueNode;
struct ASTJsonNode;
struct ASTArrayNode;
struct ASTObjectNode;
struct ASTBooleanNode;
struct ASTNumberNode;
struct ASTStringNode;

struct ASTValueNode
{
    ASTValueType type = ASTValueType::None;
};

struct ASTJsonNode : public ASTValueNode
{
    ASTArrayNode* array = nullptr;
    ASTObjectNode* object = nullptr;
};

struct ASTArrayNode : public ASTValueNode
{
    std::vector<ASTValueNode*>* values;
};

struct ASTObjectNode : public ASTValueNode
{
    std::unordered_map<std::string, ASTValueNode*>* values;
};

struct ASTPrimNode : public ASTValueNode
{
    std::string prim;
};

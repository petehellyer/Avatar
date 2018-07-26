// namespaces are used in packages generated for each language
namespace csharp avatar_interop
namespace py avatar_interop

// you can name your own types and rename the built-in ones.
typedef i32 int

service AvatarIO {

    bool Visual_L(1:bool vis),
    bool Visual_R(1:bool vis),
    bool Somatosensory_L(1:bool somat1),
    bool Somatosensory_R(1:bool somat),
    bool RewardSignal(1:bool psneg),
    bool SalienceSignal(1:bool psneg),
    double GetFwd(),
    double GetRot(),
    bool SendPosition(1:double posx, 2:double posy),
    list<double> GetStates(),
    list<double> GetNodeLocation(1:int nodeid),
    int GetNodeNumber(),
    int NextSimulation(),
    bool SendNextUnityCondition(1:bool condition)
}

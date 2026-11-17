// Exact finite-key search for a regular language of decimal word encodings.
// No heuristic language score, state budget, key cap, or plaintext repair.
#include <algorithm>
#include <array>
#include <cstdint>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;

struct TrieNode {
    array<int,10> child;
    bool terminal=false;
    TrieNode(){child.fill(-1);}
};
struct VectorHash {
    size_t operator()(const vector<int>& v) const {
        size_t h=1469598103934665603ULL;
        for(int x:v){h^=static_cast<size_t>(x)+1;h*=1099511628211ULL;}
        return h;
    }
};
struct State {
    vector<int> nodes;
    array<int,10> next;
    bool accept;
    explicit State(vector<int> v):nodes(move(v)),accept(!nodes.empty()&&nodes[0]==0){next.fill(-2);}
};
class DictionaryDFA {
    vector<TrieNode> trie{TrieNode()};
    vector<State> states;
    unordered_map<vector<int>,int,VectorHash> ids;
public:
    explicit DictionaryDFA(const vector<string>& words){
        for(const string& w:words){
            if(w.empty())throw runtime_error("empty dictionary code");
            int n=0;
            for(char c:w){
                if(c<'0'||c>'9')throw runtime_error("nondecimal dictionary code");
                int d=c-'0';
                if(trie[n].child[d]<0){int j=static_cast<int>(trie.size());trie.emplace_back();trie[n].child[d]=j;}
                n=trie[n].child[d];
            }
            trie[n].terminal=true;
        }
        states.emplace_back(vector<int>{0});ids.emplace(vector<int>{0},0);
    }
    int step(int s,int digit){
        if(s<0)return -1;
        int cached=states[s].next[digit];if(cached!=-2)return cached;
        vector<int> dest;bool terminal=false;
        for(int n:states[s].nodes){int c=trie[n].child[digit];if(c>=0){dest.push_back(c);terminal|=trie[c].terminal;}}
        if(terminal)dest.push_back(0);
        if(dest.empty()){states[s].next[digit]=-1;return -1;}
        sort(dest.begin(),dest.end());dest.erase(unique(dest.begin(),dest.end()),dest.end());
        auto it=ids.find(dest);int answer;
        if(it!=ids.end())answer=it->second;
        else {answer=static_cast<int>(states.size());ids.emplace(dest,answer);states.emplace_back(move(dest));}
        states[s].next[digit]=answer;return answer;
    }
    bool accepting(int s)const{return s>=0&&states[s].accept;}
    size_t size()const{return states.size();}
};
struct Task {
    string id;int period,feedback;
    vector<string> groups;
};
static uint64_t pow10(int n){uint64_t value=1;while(n--)value*=10;return value;}

static void solve(DictionaryDFA& dfa,const Task& task){
    int p=task.period;
    if(p<1||p>8||(task.feedback!=0&&task.feedback!=1)||task.groups.empty())throw runtime_error("invalid task");
    if(task.id.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")!=string::npos)throw runtime_error("invalid task id");
    vector<vector<int>> adjusted;vector<int> offset;
    int previous=0,position=0,selected=-1;
    for(size_t gi=0;gi<task.groups.size();++gi){
        const auto& raw=task.groups[gi];if(raw.empty())throw runtime_error("empty group");
        offset.push_back(position);vector<int> digits;
        for(char c:raw){if(c<'0'||c>'9')throw runtime_error("nondecimal group");int v=c-'0';digits.push_back((v-task.feedback*previous+10)%10);previous=v;++position;}
        adjusted.push_back(move(digits));
        if(static_cast<int>(raw.size())>=p&&(selected<0||raw.size()<task.groups[selected].size()))selected=static_cast<int>(gi);
    }
    if(selected<0)throw runtime_error("no fragment long enough to identify all key slots");
    array<int,8> key{};vector<string> found;
    uint64_t nodes=0,checked=0,pruned=0,first_pass=0;
    auto finish=[&](int gi,int start,int state){
        for(size_t j=start;j<adjusted[gi].size();++j){
            int d=(adjusted[gi][j]-key[(offset[gi]+j)%p]+10)%10;
            state=dfa.step(state,d);if(state<0)return false;
        }
        return dfa.accepting(state);
    };
    function<void(int,int)> visit=[&](int depth,int state){
        ++nodes;
        if(depth==p){
            ++checked;if(!finish(selected,p,state))return;++first_pass;
            for(size_t gi=0;gi<adjusted.size();++gi)if(static_cast<int>(gi)!=selected&&!finish(static_cast<int>(gi),0,0))return;
            string text;for(int i=0;i<p;++i)text+=char('0'+key[i]);found.push_back(text);return;
        }
        for(int d=0;d<10;++d){
            int next=dfa.step(state,d);
            if(next<0){pruned+=pow10(p-depth-1);continue;}
            key[(offset[selected]+depth)%p]=(adjusted[selected][depth]-d+10)%10;
            visit(depth+1,next);
        }
    };
    visit(0,0);
    if(checked+pruned!=pow10(p))throw runtime_error("coverage identity failed");
    sort(found.begin(),found.end());
    if(adjacent_find(found.begin(),found.end())!=found.end())throw runtime_error("duplicate full key");
    cout<<"{\"id\":\""<<task.id<<"\",\"period\":"<<p<<",\"feedback\":"<<task.feedback
        <<",\"selected_fragment\":"<<selected<<",\"complete\":true,\"domain_keys\":"<<pow10(p)
        <<",\"checked_keys\":"<<checked<<",\"prefix_pruned_keys\":"<<pruned<<",\"prefix_nodes\":"<<nodes
        <<",\"selected_fragment_pass_keys\":"<<first_pass<<",\"dfa_states\":"<<dfa.size()<<",\"keys\":[";
    for(size_t i=0;i<found.size();++i){if(i)cout<<',';cout<<'"'<<found[i]<<'"';}
    cout<<"]}"<<endl;
}
int main(){
    try {
        string magic;size_t n;
        if(!(cin>>magic>>n)||magic!="R22V1"||n==0)throw runtime_error("invalid header");
        vector<string> words(n);for(auto& w:words)if(!(cin>>w))throw runtime_error("missing dictionary");
        DictionaryDFA dfa(words);
        size_t count;if(!(cin>>count))throw runtime_error("missing task count");
        for(size_t i=0;i<count;++i){Task task;size_t groups;
            if(!(cin>>task.id>>task.period>>task.feedback>>groups))throw runtime_error("missing task header");
            task.groups.resize(groups);for(auto& g:task.groups)if(!(cin>>g))throw runtime_error("missing group");
            solve(dfa,task);
        }
        string extra;if(cin>>extra)throw runtime_error("unexpected trailing input");
        return 0;
    }catch(const exception& e){cerr<<e.what()<<endl;return 1;}
}

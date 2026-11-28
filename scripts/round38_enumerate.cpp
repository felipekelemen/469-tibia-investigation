// Exact anchored digit-morphism enumeration. No semantic score or text repair.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

using Key = std::array<uint16_t,10>;
struct Node {std::array<int,26> next{}; bool terminal=false;};
std::vector<Node> trie(1);
std::array<std::string,19683> units;
std::vector<std::string> groups;
std::set<Key> solutions;
uint64_t states=0,visits=0;
constexpr uint64_t STATE_CAP=2000000, VISIT_CAP=5000000, KEY_CAP=100000;

void insert(std::string const& s) {
 int node=0;
 for(char c:s){
  if(c<'A'||c>'Z')throw std::runtime_error("invalid_lexicon");
  int i=c-'A', child=trie[node].next[i];
  if(!child){child=trie.size();trie[node].next[i]=child;trie.emplace_back();}
  node=child;
 }
 trie[node].terminal=true;
}
int follow(int node,std::string const& unit){
 for(char c:unit){node=trie[node].next[c-'A'];if(!node)return -1;}
 return node;
}
bool lexical(std::string const& raw,Key const& key){
 int node=0;
 for(char c:raw){node=follow(node,units[key[c-'0']]);if(node<0)return false;}
 return trie[node].terminal;
}
uint16_t code(std::string const& s){
 uint16_t n=0;for(char c:s)n=n*27+c-'A'+1;units[n]=s;return n;
}

// Follow actual dictionary edges; repeated digits reuse their exact unit.
void extensions(std::string const& raw,Key key,std::function<void(Key const&)> const& accept){
 std::function<void(size_t,int)> visit;
 visit=[&](size_t pos,int node){
  if(++visits>VISIT_CAP)throw std::runtime_error("local_visit_limit");
  if(pos==raw.size()){if(trie[node].terminal)accept(key);return;}
  int d=raw[pos]-'0';
  if(key[d]){int next=follow(node,units[key[d]]);if(next>=0)visit(pos+1,next);return;}
  std::function<void(int,std::string const&)> chunk=[&](int here,std::string const& prefix){
   if(prefix.size()==3)return;
   for(int c=0;c<26;c++){
    int next=trie[here].next[c];if(!next)continue;
    std::string unit=prefix+char('A'+c);key[d]=code(unit);visit(pos+1,next);key[d]=0;
    chunk(next,unit);
   }
  };chunk(node,"");
 };
 visit(0,0);
}

void search(Key const& key){
 if(++states>STATE_CAP)throw std::runtime_error("state_limit");
 int choice=-1;
 std::tuple<double,int,int,std::string> best{2.,100,100,""};
 for(size_t i=0;i<groups.size();i++){
  std::set<char> missing;int known=0;
  for(char c:groups[i]){if(key[c-'0'])known++;else missing.insert(c);}
  if(missing.empty()){if(!lexical(groups[i],key))return;continue;}
  auto score=std::make_tuple(-double(known)/groups[i].size(),int(missing.size()),int(groups[i].size()),groups[i]);
  if(score<best){best=score;choice=i;}
 }
 if(choice<0){
  solutions.insert(key);if(solutions.size()>KEY_CAP)throw std::runtime_error("key_limit");return;
 }
 extensions(groups[choice],key,[&](Key const& next){search(next);});
}

void print_key(Key const& key){
 std::cout<<'[';for(int d=0;d<10;d++){if(d)std::cout<<',';std::cout<<key[d];}std::cout<<']';
}

int main(int argc,char** argv){
 try{
  if(argc!=4)throw std::runtime_error("usage_lexicon_case_emitkeys");
  std::ifstream lex(argv[1]),input(argv[2]);if(!lex||!input)throw std::runtime_error("input_unavailable");
  std::set<std::string> vocabulary;std::string form;
  while(lex>>form){vocabulary.insert(form);insert(form);}
  int n,anchor;if(!(input>>n>>anchor>>form)||n<1||n>50||anchor<0||anchor>=n)throw std::runtime_error("invalid_case");
  std::string anchor_word=form,anchor_raw;
  for(int i=0;i<n;i++){
   std::string raw;if(!(input>>raw)||raw.empty()||raw.size()>40||raw.find_first_not_of("0123456789")!=std::string::npos)throw std::runtime_error("invalid_group");
   groups.push_back(raw);if(i==anchor)anchor_raw=raw;
  }
  std::sort(groups.begin(),groups.end());groups.erase(std::unique(groups.begin(),groups.end()),groups.end());
  if(vocabulary.count(anchor_word)){
   // Independent anchor partition recursion, then exact trie search.
   Key key{};
   std::function<void(size_t,size_t)> partition=[&](size_t i,size_t j){
    if(i==anchor_raw.size()){if(j==anchor_word.size())search(key);return;}
    int d=anchor_raw[i]-'0';
    if(key[d]){auto const& u=units[key[d]];if(anchor_word.compare(j,u.size(),u)==0)partition(i+1,j+u.size());return;}
    for(size_t len=1;len<=3&&j+len<=anchor_word.size();len++){
     key[d]=code(anchor_word.substr(j,len));partition(i+1,j+len);key[d]=0;
    }
   };partition(0,0);
  }
  std::cout<<"{\"complete\":true,\"count\":"<<solutions.size()<<",\"states\":"<<states<<",\"local_visits\":"<<visits<<",\"keys\":[";
  if(std::string(argv[3])=="1"){bool first=true;for(auto const& key:solutions){if(!first)std::cout<<',';first=false;print_key(key);}}
  std::cout<<"]}\n";
 }catch(std::exception const& e){
  std::cout<<"{\"complete\":false,\"count\":null,\"reason\":\""<<e.what()<<"\",\"partial_keys\":"<<solutions.size()<<"}\n";
 }
}

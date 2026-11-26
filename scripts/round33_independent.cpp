// Post-fit independent contraction for the unchanged seven Knightmare groups.
// Local generator traverses a word and branches on units, not length vectors.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
using Key=std::array<std::string,10>;
using Triple=std::array<std::string,3>;
using Pair=std::array<std::string,2>;
using Count=unsigned __int128;
std::string decimal(Count n){if(!n)return "0";std::string s;while(n){s+=char('0'+n%10);n/=10;}std::reverse(s.begin(),s.end());return s;}

template<class Callback>
void all(std::string const& raw,std::vector<std::string> const& words,Callback accept){
 for(auto const& form:words){
  if(form.size()<raw.size() || form.size()>3*raw.size())continue;
  Key key{};
  std::function<void(size_t,size_t)> visit=[&](size_t i,size_t pos){
   if(i==raw.size()){if(pos==form.size())accept(key);return;}
   size_t remain=raw.size()-i;
   if(form.size()-pos<remain || form.size()-pos>3*remain)return;
   int d=raw[i]-'0';
   if(!key[d].empty()){
    if(form.compare(pos,key[d].size(),key[d])==0)visit(i+1,pos+key[d].size());
    return;
   }
   for(size_t n=1;n<=3 && pos+n<=form.size();n++){
    key[d]=form.substr(pos,n);visit(i+1,pos+n);key[d].clear();
   }
  };visit(0,0);
 }
}

int main(int argc,char** argv){
 if(argc!=2)return 2;
 std::ifstream input(argv[1]);if(!input)return 2;
 std::set<std::string> unique;std::string w;while(input>>w)unique.insert(w);
 std::vector<std::string> words(unique.begin(),unique.end());
 std::map<Pair,uint64_t> leaf5;
 std::map<Pair,std::vector<std::string>> rows3;
 std::map<Triple,std::vector<std::string>> rows8;
 std::map<Triple,uint64_t> leaf01;
 std::array<uint64_t,5> generated{};
 all("345",words,[&](Key const& k){leaf5[{k[3],k[4]}]++;generated[0]++;});
 all("3466",words,[&](Key const& k){rows3[{k[4],k[6]}].push_back(k[3]);generated[1]++;});
 all("3478",words,[&](Key const& k){rows8[{k[3],k[4],k[7]}].push_back(k[8]);generated[2]++;});
 all("90871",words,[&](Key const& k){if(unique.count(k[0])){leaf01[{k[9],k[8],k[7]}]++;generated[3]++;}});
 Count total=0;uint64_t successful_core_extensions=0;
 all("97664",words,[&](Key const& k){
  generated[4]++;
  if(!unique.count(k[6]+k[7]))return;
  auto a=rows3.find({k[4],k[6]});if(a==rows3.end())return;
  for(auto const& unit3:a->second){
   auto leaf=leaf5.find({unit3,k[4]});if(leaf==leaf5.end())continue;
   auto b=rows8.find({unit3,k[4],k[7]});if(b==rows8.end())continue;
   for(auto const& unit8:b->second){
    auto c=leaf01.find({k[9],unit8,k[7]});if(c==leaf01.end())continue;
    total+=Count(leaf->second)*c->second;successful_core_extensions++;
   }
  }
 });
 // At most18278^9assignments exist for nine observed digits, below2^128.
 std::cout<<"{\"complete\":true,\"count\":\""<<decimal(total)<<"\",\"observed_digits\":9,\"successful_core_extensions\":"<<successful_core_extensions<<",\"local_assignment_counts\":[";
 for(size_t i=0;i<generated.size();i++){if(i)std::cout<<",";std::cout<<generated[i];}
 std::cout<<"],\"local_order\":[\"345\",\"3466\",\"3478\",\"90871_with_lexical0\",\"97664\"]}\n";
}

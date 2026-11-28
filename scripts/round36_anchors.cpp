// Exact conditional word marginals for Knightmare's seven digit scopes.
// Does not score English, infer semantics or fill the absent digit 2.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using Key=std::array<uint16_t,10>;
using Pair=std::array<uint16_t,2>;
using Triple=std::array<uint16_t,3>;
using Count=unsigned __int128;
std::array<std::string,19683> units;
std::array<std::string,7> raw;
std::array<uint64_t,5> local_rows{};
uint64_t core_visits=0,successful_core=0;
constexpr uint64_t LOCAL_CAP=3000000,CORE_CAP=20000000;

std::string decimal(Count n){if(!n)return "0";std::string s;while(n){s+=char('0'+n%10);n/=10;}std::reverse(s.begin(),s.end());return s;}
uint16_t encode(std::string const& s){uint16_t n=0;for(char c:s)n=27*n+c-'A'+1;units[n]=s;return n;}
std::string emit(std::string const& s,Key const& key){std::string out;for(char c:s){if(!key[c-'0'])throw std::runtime_error("missing_digit");out+=units[key[c-'0']];}return out;}
std::string signature(Key const& key){std::string out;for(auto const& r:raw){out+=emit(r,key);out+=' ';}return out;}
int mask(std::string const& s){int m=0;for(char c:s){if(c<'0'||c>'9')throw std::runtime_error("invalid_digit");m|=1<<(c-'0');}return m;}

template<class Callback>
void all(std::string const& input,std::vector<std::string> const& words,int table,Callback accept){
 for(auto const& form:words){
  if(form.size()<input.size() || form.size()>3*input.size())continue;
  Key key{};
  std::function<void(size_t,size_t)> visit=[&](size_t i,size_t pos){
   if(i==input.size()){
    if(pos==form.size()){if(++local_rows[table]>LOCAL_CAP)throw std::runtime_error("local_limit");accept(key);}return;
   }
   size_t remain=input.size()-i;
   if(form.size()-pos<remain || form.size()-pos>3*remain)return;
   int d=input[i]-'0';
   if(key[d]){auto const& unit=units[key[d]];if(form.compare(pos,unit.size(),unit)==0)visit(i+1,pos+unit.size());return;}
   for(size_t n=1;n<=3 && pos+n<=form.size();n++){key[d]=encode(form.substr(pos,n));visit(i+1,pos+n);key[d]=0;}
  };visit(0,0);
 }
}

struct Entry{Count count=0;Key first{},second{};std::string first_text;};
std::array<std::map<std::string,Entry>,7> histograms;
void record(int group,Count weight,Key const& key){
 auto& row=histograms[group][emit(raw[group],key)];
 if(!row.first[0]){row.first=key;row.first_text=signature(key);}
 else if(!row.second[0] && signature(key)!=row.first_text)row.second=key;
 if(row.count>~Count(0)-weight)throw std::runtime_error("count_overflow");row.count+=weight;
}
void print_key(Key const& k){std::cout<<'[';for(int d=0;d<10;d++){if(d)std::cout<<',';std::cout<<k[d];}std::cout<<']';}

int main(int argc,char** argv){
 try{
  if(argc!=9)throw std::runtime_error("usage_lexicon_and_seven_groups");
  std::array<std::string,7> base={"3478","67","90871","97664","3466","0","345"};
  for(int i=0;i<7;i++){raw[i]=argv[i+2];if(mask(raw[i])!=mask(base[i]) || raw[i].size()!=base[i].size())throw std::runtime_error("unsupported_topology");}
  std::ifstream input(argv[1]);if(!input)throw std::runtime_error("input_unavailable");
  std::set<std::string> lex;std::string word;
  while(input>>word){if(word.find_first_not_of("ABCDEFGHIJKLMNOPQRSTUVWXYZ")!=std::string::npos)throw std::runtime_error("invalid_lexicon");lex.insert(word);}
  std::vector<std::string> words(lex.begin(),lex.end());
  std::map<Pair,std::vector<uint16_t>> leaf5,rows3;
  std::map<Triple,std::vector<uint16_t>> rows8;
  std::map<Triple,std::vector<Pair>> leaf01;
  all(raw[6],words,0,[&](Key const& k){leaf5[{k[3],k[4]}].push_back(k[5]);});
  all(raw[4],words,1,[&](Key const& k){rows3[{k[4],k[6]}].push_back(k[3]);});
  all(raw[0],words,2,[&](Key const& k){rows8[{k[3],k[4],k[7]}].push_back(k[8]);});
  all(raw[2],words,3,[&](Key const& k){if(lex.count(units[k[0]]))leaf01[{k[9],k[8],k[7]}].push_back({k[0],k[1]});});
  Count total=0;
  all(raw[3],words,4,[&](Key const& original){
   Key k=original;if(!lex.count(emit(raw[1],k)))return;
   auto a=rows3.find({k[4],k[6]});if(a==rows3.end())return;
   for(auto u3:a->second){
    k[3]=u3;auto l=leaf5.find({k[3],k[4]});if(l==leaf5.end())continue;
    auto b=rows8.find({k[3],k[4],k[7]});if(b==rows8.end())continue;
    for(auto u8:b->second){
     if(++core_visits>CORE_CAP)throw std::runtime_error("core_limit");
     k[8]=u8;auto c=leaf01.find({k[9],k[8],k[7]});if(c==leaf01.end())continue;
     successful_core++;auto const& left=l->second;auto const& right=c->second;
     Count weight=Count(left.size())*right.size();total+=weight;
     k[5]=left[0];k[0]=right[0][0];k[1]=right[0][1];
     for(int g:{0,1,3,4})record(g,weight,k);
     // Each distinct5 changes word345. Distinct(0,1)changes word0or90871.
     // Thus two representatives certify variation of the Cartesian product.
     if(left.size()>1 || right.size()>1){
      Key alt=k;if(left.size()>1)alt[5]=left[1];else{alt[0]=right[1][0];alt[1]=right[1][1];}
      for(int g:{0,1,3,4})record(g,0,alt);
     }
     for(auto u5:left){
      k[5]=u5;k[0]=right[0][0];k[1]=right[0][1];record(6,right.size(),k);
      if(right.size()>1){Key alt=k;alt[0]=right[1][0];alt[1]=right[1][1];record(6,0,alt);}
     }
     for(auto pair:right){
      k[0]=pair[0];k[1]=pair[1];k[5]=left[0];record(2,left.size(),k);record(5,left.size(),k);
      if(left.size()>1){Key alt=k;alt[5]=left[1];record(2,0,alt);record(5,0,alt);}
     }
    }
   }
  });
  std::cout<<"{\"complete\":true,\"count\":\""<<decimal(total)<<"\",\"successful_core_extensions\":"<<successful_core<<",\"core_visits\":"<<core_visits<<",\"marginals\":[";
  for(int g=0;g<7;g++){
   if(g)std::cout<<',';std::cout<<"{\"raw\":\""<<raw[g]<<"\",\"rows\":[";bool first=true;Count sum=0;
   for(auto const& item:histograms[g]){auto const& r=item.second;sum+=r.count;if(!first)std::cout<<',';first=false;
    std::cout<<"[\""<<item.first<<"\",\""<<decimal(r.count)<<"\",";print_key(r.first);std::cout<<',';
    if(r.second[0])print_key(r.second);else std::cout<<"null";std::cout<<']';}
   if(sum!=total)throw std::runtime_error("marginal_sum_disagrees");std::cout<<"]}";
  }
  std::cout<<"]}\n";
 }catch(std::bad_alloc const&){std::cout<<"{\"complete\":false,\"count\":null,\"reason\":\"memory_limit\"}\n";}
 catch(std::exception const& e){std::cout<<"{\"complete\":false,\"count\":null,\"reason\":\""<<e.what()<<"\"}\n";}
}

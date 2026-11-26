// Exact finite relation counting. No language scoring or semantic claims.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <limits>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>
using Count=unsigned __int128;
using Key=std::array<uint16_t,10>;
constexpr size_t ROW_CAP=6000000, LIVE_CAP=12000000;
constexpr uint64_t PAIR_CAP=100000000;
struct Hash { size_t operator()(Key const& k)const {size_t h=1469598103934665603ULL;for(auto v:k){h^=v;h*=1099511628211ULL;}return h;} };
using Table=std::unordered_map<Key,Count,Hash>;
struct Factor {int mask=0;Table rows;};
uint64_t visits=0;size_t peak=0;
Count add(Count a,Count b){if(a>~Count(0)-b)throw std::runtime_error("arithmetic_limit");return a+b;}
Count mul(Count a,Count b){if(b && a>~Count(0)/b)throw std::runtime_error("arithmetic_limit");return a*b;}
std::string decimal(Count n){if(!n)return "0";std::string s;while(n){s+=char('0'+n%10);n/=10;}std::reverse(s.begin(),s.end());return s;}
Key project(Key k,int mask){for(int d=0;d<10;d++)if(!(mask&(1<<d)))k[d]=0;return k;}
void insert(Table& t,Key const& k,Count value){auto it=t.find(k);if(it==t.end()){if(t.size()>=ROW_CAP)throw std::runtime_error("table_row_limit");t.emplace(k,value);peak=std::max(peak,t.size());}else it->second=add(it->second,value);}
int maskof(std::string const& s){int m=0;for(char c:s){if(c<'0'||c>'9')throw std::runtime_error("invalid_input");m|=1<<(c-'0');}return m;}
uint16_t encode(std::string const& s,int pos,int len){uint16_t n=0;for(int i=0;i<len;i++)n=n*27+(s[pos+i]-'A'+1);return n;}

Factor local(std::string const& raw,std::vector<std::vector<std::string>> const& bylen,int private_mask){
 Factor f;int original=maskof(raw);f.mask=original&~private_mask;
 std::vector<int> ds;for(int d=0;d<10;d++)if(original&(1<<d))ds.push_back(d);
 std::array<int,10> len{};
 std::function<void(size_t)> walk=[&](size_t i){
  if(i<ds.size()){for(int n=1;n<=3;n++){len[ds[i]]=n;walk(i+1);}return;}
  int total=0;for(char c:raw)total+=len[c-'0'];if(total>=int(bylen.size()))return;
  for(auto const& form:bylen[total]){
   Key key{};int pos=0;bool ok=true;
   for(char c:raw){int d=c-'0',n=len[d];auto unit=encode(form,pos,n);pos+=n;
    if(key[d] && key[d]!=unit){ok=false;break;}key[d]=unit;}
   // Unique word forms + fixed length assignment yield each local key once.
   if(ok)insert(f.rows,project(key,f.mask),1);
  }
 };walk(0);return f;
}

Factor join(Factor const& a,Factor const& b,int eliminate=-1){
 int common=a.mask&b.mask;Factor out;out.mask=a.mask|b.mask;
 if(eliminate>=0)out.mask&=~(1<<eliminate);
 if(a.rows.empty()||b.rows.empty())return out;
 auto const* small=&a;auto const* large=&b;if(a.rows.size()>b.rows.size())std::swap(small,large);
 using Row=Table::value_type;
 std::unordered_map<Key,std::vector<Row const*>,Hash> index;
 for(auto const& row:small->rows)index[project(row.first,common)].push_back(&row);
 for(auto const& left:large->rows){
  auto it=index.find(project(left.first,common));if(it==index.end())continue;
  for(auto right:it->second){
   if(++visits>PAIR_CAP)throw std::runtime_error("join_pair_limit");
   Key merged=left.first;for(int d=0;d<10;d++)if(small->mask&(1<<d))merged[d]=right->first[d];
   insert(out.rows,project(merged,out.mask),mul(left.second,right->second));
  }
 }return out;
}
Factor sum_out(Factor const& f,int d){Factor out;out.mask=f.mask&~(1<<d);for(auto const& row:f.rows)insert(out.rows,project(row.first,out.mask),row.second);return out;}
void live_check(std::vector<Factor> const& fs){size_t n=0;for(auto const& f:fs)n+=f.rows.size();if(n>LIVE_CAP)throw std::runtime_error("live_factor_limit");}
int choose(std::vector<Factor> const& fs){
 int active=0;std::array<int,10> edges{};
 for(auto const& f:fs){active|=f.mask;for(int d=0;d<10;d++)if(f.mask&(1<<d))edges[d]|=f.mask&~(1<<d);}
 std::tuple<int,int,size_t,int> best{1000,1000,std::numeric_limits<size_t>::max(),-1};
 for(int d=0;d<10;d++)if(active&(1<<d)){
  int ns=edges[d],fill=0;for(int a=0;a<10;a++)if(ns&(1<<a))for(int b=a+1;b<10;b++)if((ns&(1<<b)) && !(edges[a]&(1<<b)))fill++;
  size_t size=0;for(auto const& f:fs)if(f.mask&(1<<d))size+=f.rows.size();
  best=std::min(best,std::make_tuple(fill,__builtin_popcount(unsigned(ns)),size,d));
 }return std::get<3>(best);
}
Count reduce(std::vector<Factor> fs,std::vector<int>& order){
 while(true){
  for(auto const& f:fs)if(f.rows.empty())return 0;
  int d=choose(fs);if(d<0)break;order.push_back(d);
  std::vector<Factor> bucket,rest;
  for(auto& f:fs){if(f.mask&(1<<d))bucket.push_back(std::move(f));else rest.push_back(std::move(f));}
  std::stable_sort(bucket.begin(),bucket.end(),[](Factor const& a,Factor const& b){return a.rows.size()<b.rows.size();});
  Factor current=std::move(bucket[0]);
  if(bucket.size()==1)current=sum_out(current,d);
  else for(size_t i=1;i<bucket.size();i++){
   // All bucket factors share d. Preserve d until the last join, then sum it.
   current=join(current,bucket[i],i+1==bucket.size()?d:-1);
   bucket[i].rows.clear();if(current.rows.empty())return 0;
  }
  rest.push_back(std::move(current));fs=std::move(rest);live_check(fs);
 }
 Count result=1;for(auto const& f:fs){Count subtotal=0;for(auto const& r:f.rows)subtotal=add(subtotal,r.second);result=mul(result,subtotal);}return result;
}

int main(int argc,char** argv){
 try{
  if(argc==2 && std::string(argv[1])=="--arithmetic-test"){
   bool a=false,b=false;try{add(~Count(0),1);}catch(...){a=true;}try{mul(~Count(0),2);}catch(...){b=true;}
   if(!a||!b||decimal(add(Count(1)<<100,7))!="1267650600228229401496703205383")return 2;
   std::cout<<"arithmetic overflow guards passed\n";return 0;
  }
  if(argc!=3)throw std::runtime_error("usage");
  std::ifstream lex(argv[1]),input(argv[2]);if(!lex||!input)throw std::runtime_error("input_unavailable");
  std::set<std::string> unique;std::string word;
  while(lex>>word){if(word.empty()||word.find_first_not_of("ABCDEFGHIJKLMNOPQRSTUVWXYZ")!=std::string::npos)throw std::runtime_error("invalid_lexicon");unique.insert(word);}
  std::vector<std::vector<std::string>> bylen(64);for(auto const& s:unique){if(s.size()>=bylen.size())bylen.resize(s.size()+1);bylen[s.size()].push_back(s);}
  int n=0;if(!(input>>n)||n<1||n>50)throw std::runtime_error("invalid_input");
  std::vector<std::pair<std::string,std::string>> words;std::set<std::string> seen;
  for(int i=0;i<n;i++){std::string raw,forced;if(!(input>>raw>>forced)||raw.empty()||raw.size()>30)throw std::runtime_error("invalid_input");maskof(raw);
   if(!seen.insert(raw).second)throw std::runtime_error("duplicate_group_input");
   words.push_back({raw,forced});}
  std::array<int,10> degree{};int observed=0;
  for(auto const& r:words){int m=maskof(r.first);observed|=m;for(int d=0;d<10;d++)if(m&(1<<d))degree[d]++;}
  int priv=0;for(int d=0;d<10;d++)if(degree[d]==1)priv|=1<<d;
  std::stable_sort(words.begin(),words.end(),[](auto const& a,auto const& b){return std::make_tuple(__builtin_popcount(unsigned(maskof(a.first))),a.first)<std::make_tuple(__builtin_popcount(unsigned(maskof(b.first))),b.first);});
  std::vector<Factor> factors;std::vector<std::tuple<std::string,int,size_t>> localstats;
  bool empty=false;
  for(auto const& r:words){
   std::vector<std::vector<std::string>> restricted;
   auto const* bank=&bylen;
   if(r.second!="-"){restricted.resize(r.second.size()+1);if(unique.count(r.second))restricted.back().push_back(r.second);bank=&restricted;}
   auto f=local(r.first,*bank,priv);localstats.push_back({r.first,f.mask,f.rows.size()});empty=f.rows.empty();factors.push_back(std::move(f));live_check(factors);if(empty)break;
  }
  std::vector<int> order;Count total=empty?0:reduce(std::move(factors),order);
  std::cout<<"{\"complete\":true,\"count\":\""<<decimal(total)<<"\",\"observed_mask\":"<<observed<<",\"private_mask\":"<<priv<<",\"pair_visits\":"<<visits<<",\"peak_table_rows\":"<<peak<<",\"elimination_order\":[";
  for(size_t i=0;i<order.size();i++){if(i)std::cout<<",";std::cout<<order[i];}
  std::cout<<"],\"local_tables\":[";
  for(size_t i=0;i<localstats.size();i++){if(i)std::cout<<",";auto [raw,mask,size]=localstats[i];std::cout<<"{\"raw\":\""<<raw<<"\",\"remaining_mask\":"<<mask<<",\"rows\":"<<size<<"}";}
  std::cout<<"]}\n";
 }catch(std::bad_alloc const&){std::cout<<"{\"complete\":false,\"count\":null,\"reason\":\"memory_limit\"}\n";}
 catch(std::exception const& e){std::cout<<"{\"complete\":false,\"count\":null,\"reason\":\""<<e.what()<<"\"}\n";}
}

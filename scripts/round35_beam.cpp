// Fixed digit-unit beam search. Scores rank candidates; no uniqueness claim.
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using Key = std::array<uint16_t, 10>;
struct KeyHash { size_t operator()(Key const& k) const {
    size_t h=1469598103934665603ULL;
    for(auto n:k)h=(h^n)*1099511628211ULL;
    return h;
}};
struct Row { Key key{}; int word=0; };
struct Node { Key key{}; std::vector<int> words; double score=0; };
uint16_t unit(std::string const& s) { uint16_t n=0;for(char c:s)n=n*27+c-'a'+1;return n; }
std::string spell(uint16_t n) { std::string s;while(n){s+=char('a'+n%27-1);n/=27;}std::reverse(s.begin(),s.end());return s; }
bool better(Node const& a,Node const& b){return a.score!=b.score?a.score>b.score:a.key<b.key;}
uint64_t pairid(int a,int b){return (uint64_t(uint32_t(a))<<32)|uint32_t(b);}

int main(int argc,char** argv){
    if(argc<8)return 2;
    std::ifstream in(argv[1]);if(!in)return 2;
    size_t beam=std::stoull(argv[2]),rowcap=std::stoull(argv[3]);
    uint64_t checkcap=std::stoull(argv[4]),extensioncap=std::stoull(argv[5]);
    double seconds=std::stod(argv[6]);
    if(!beam || !rowcap || !checkcap || !extensioncap || seconds<=0)return 2;
    size_t size;in>>size;
    std::vector<std::string> words(size);
    std::vector<double> count(size),unigram(size);
    double total=0;
    for(size_t i=0;i<size;i++){in>>words[i]>>count[i];if(i)total+=count[i];}
    std::unordered_map<uint64_t,double> pairs;
    size_t np;in>>np;
    for(size_t i=0;i<np;i++){int a,b;double c;in>>a>>b>>c;pairs[pairid(a,b)]=c;}
    if(!in)return 2;
    const double alpha=.1,V=double(size-1);
    for(size_t i=1;i<size;i++)unigram[i]=std::log((count[i]+alpha)/(total+alpha*V));
    auto score=[&](int prev,int next){
        auto it=pairs.find(pairid(prev,next));double c=it==pairs.end()?0:it->second;
        return .35*unigram[next]+.65*std::log((c+alpha)/(count[prev]+alpha*V));
    };
    std::vector<std::string> groups;
    for(int i=7;i<argc;i++){
        std::string g=argv[i];
        if(g.empty() || g.find_first_not_of("0123456789")!=std::string::npos)return 2;
        groups.push_back(g);
    }
    auto start=std::chrono::steady_clock::now();
    uint64_t visits=0,checks=0,pruned=0,extensions=0,generated=0;
    auto clockcheck=[&](){
        if(std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>seconds)
            throw std::runtime_error("time");
    };
    std::unordered_map<std::string,std::vector<Row>> cache;
    std::vector<Node> current(1);
    std::string status="ranked",reason;
    try {
        for(std::string const& raw:groups){
            auto found=cache.find(raw);
            if(found==cache.end()){
                std::vector<Row> rows;
                for(size_t wi=1;wi<size;wi++){
                    auto const& form=words[wi];
                    if(form.size()<raw.size() || form.size()>3*raw.size())continue;
                    Key key{};
                    std::function<void(size_t,size_t)> walk=[&](size_t i,size_t p){
                        if((++visits&4095)==0)clockcheck();
                        if(i==raw.size()){
                            if(p==form.size()){
                                if(rows.size()>=rowcap)throw std::runtime_error("local_rows");
                                rows.push_back({key,int(wi)});generated++;
                            }
                            return;
                        }
                        size_t remain=raw.size()-i;
                        if(form.size()-p<remain || form.size()-p>3*remain)return;
                        int digit=raw[i]-'0';
                        if(key[digit]){
                            auto u=spell(key[digit]);
                            if(form.compare(p,u.size(),u)==0)walk(i+1,p+u.size());
                            return;
                        }
                        for(size_t n=1;n<=3 && p+n<=form.size();n++){
                            key[digit]=unit(form.substr(p,n));walk(i+1,p+n);key[digit]=0;
                        }
                    };
                    walk(0,0);
                }
                found=cache.emplace(raw,std::move(rows)).first;
            }
            if(found->second.empty()){status="empty_local_domain";current.clear();break;}
            std::vector<Node> next;
            std::unordered_set<Key,KeyHash> seen;
            for(auto const& parent:current)for(auto const& row:found->second){
                if(++checks>checkcap)throw std::runtime_error("compatibility_checks");
                if((checks&4095)==0)clockcheck();
                bool compatible=true;
                for(int d=0;d<10;d++)if(parent.key[d] && row.key[d] && parent.key[d]!=row.key[d]){
                    compatible=false;break;
                }
                if(!compatible)continue;
                Key key=parent.key;
                for(int d=0;d<10;d++)if(row.key[d])key[d]=row.key[d];
                if(!seen.insert(key).second)continue;
                if(seen.size()>extensioncap)throw std::runtime_error("extensions");
                Node node=parent;node.key=key;
                node.score+=score(parent.words.empty()?0:parent.words.back(),row.word);
                node.words.push_back(row.word);next.push_back(std::move(node));extensions++;
            }
            if(next.empty()){status="no_candidate_in_beam";current.clear();break;}
            if(next.size()>beam){
                pruned+=next.size()-beam;
                std::nth_element(next.begin(),next.begin()+beam,next.end(),better);next.resize(beam);
            }
            std::sort(next.begin(),next.end(),better);current=std::move(next);
        }
    } catch(std::runtime_error const& error){status="limit";reason=error.what();current.clear();}
    std::cout.precision(17);
    std::cout<<"{\"status\":\""<<status<<"\",\"limit\":\""<<reason
             <<"\",\"checks\":"<<checks<<",\"local_visits\":"<<visits
             <<",\"generated_local_rows\":"<<generated<<",\"pruned\":"<<pruned
             <<",\"extensions\":"<<extensions<<",\"retained\":"<<current.size()<<",\"top\":[";
    for(size_t i=0;i<std::min(size_t(2),current.size());i++){
        if(i)std::cout<<",";
        auto const& node=current[i];
        std::cout<<"{\"score\":"<<node.score<<",\"key\":[";
        for(int d=0;d<10;d++){if(d)std::cout<<",";std::cout<<"\""<<spell(node.key[d])<<"\"";}
        std::cout<<"],\"words\":[";
        for(size_t j=0;j<node.words.size();j++){if(j)std::cout<<",";std::cout<<"\""<<words[node.words[j]]<<"\"";}
        std::cout<<"]}";
    }
    std::cout<<"]}\n";
}

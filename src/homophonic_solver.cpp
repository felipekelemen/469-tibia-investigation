// Incremental homophonic quadgram optimizer. No plaintext or holdout input.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include <map>
#include <numeric>
#include <random>
#include <vector>
struct Gram { std::array<int,4> c; int count; };
struct Engine {
 int k,n=0; const double* lm; std::vector<Gram> grams; std::vector<std::vector<int>> affected;
 std::vector<int> counts,mapping,lettercounts,marks; std::array<double,26> expected;
 int stamp=0; double total=0;
 Engine(const int* data,const int* lengths,int books,int keys,const double* table):k(keys),lm(table),affected(k),counts(k),mapping(k),lettercounts(26) {
  std::map<std::array<int,4>,int> gs;int off=0;
  for(int b=0;b<books;b++) {for(int i=0;i<lengths[b];i++) {counts[data[off+i]]++;n++;}for(int i=0;i+3<lengths[b];i++)gs[{data[off+i],data[off+i+1],data[off+i+2],data[off+i+3]}]++;off+=lengths[b];}
  for(auto &p:gs) {int idx=grams.size();grams.push_back({p.first,p.second});auto cs=p.first;std::sort(cs.begin(),cs.end());for(int j=0;j<4;j++)if(j==0||cs[j]!=cs[j-1])affected[cs[j]].push_back(idx);total+=p.second;}
  marks.assign(grams.size(),0);expected.fill(0);double norm=0;
  for(int i=0;i<26*26*26*26;i++){double v=std::pow(10.0,table[i]);expected[(i/(26*26*26))%26]+=v;norm+=v;}
  for(auto &v:expected)v/=norm;
 }
 double gram(int i) const {auto &g=grams[i];int idx=0;for(auto c:g.c)idx=idx*26+mapping[c];return lm[idx]*g.count;}
 double score() const {double s=0;for(int i=0;i<(int)grams.size();i++)s+=gram(i);return s;}
 double penalty() const {double s=0;for(int a=0;a<26;a++){double d=lettercounts[a]-expected[a]*n;s+=d*d/(expected[a]*n+5.0);}return s;}
 void recount(){std::fill(lettercounts.begin(),lettercounts.end(),0);for(int i=0;i<k;i++)lettercounts[mapping[i]]+=counts[i];}
 std::vector<int> touched(const std::vector<int>&keys){stamp++;std::vector<int> a;for(int c:keys)for(int x:affected[c])if(marks[x]!=stamp){marks[x]=stamp;a.push_back(x);}return a;}
};
extern "C" int fh_solve(const int* data,const int* lengths,int books,int k,const double* table,uint64_t seed,int restarts,int steps,double max_temp,double freq_weight,int* out,double* stats){
 if(k<1||k>256||books<1||restarts<1||steps<1)return 1;
 int cnt=0;for(int b=0;b<books;b++){if(lengths[b]<0)return 2;cnt+=lengths[b];}for(int i=0;i<cnt;i++)if(data[i]<0||data[i]>=k)return 3;
 Engine e(data,lengths,books,k,table);if(e.total==0)return 4;
 std::mt19937_64 rng(seed);auto uni=[&](){return std::generate_canonical<double,53>(rng);};auto ri=[&](int a){return (int)(rng()%a);};
 std::vector<int> active;for(int i=0;i<k;i++)if(e.counts[i])active.push_back(i);
 double best=-std::numeric_limits<double>::infinity(),best_raw=best;std::vector<int> best_map;long accepted=0;
 for(int r=0;r<restarts;r++) {
  std::fill(e.lettercounts.begin(),e.lettercounts.end(),0);
  auto order=active;std::stable_sort(order.begin(),order.end(),[&](int a,int b){return e.counts[a]>e.counts[b];});
  if(r%4==3 && !best_map.empty()){e.mapping=best_map;for(int j=0;j<std::max(3,(int)active.size()/8);j++)e.mapping[active[ri(active.size())]]=ri(26);e.recount();}
  else {
   for(int i=0;i<k;i++)e.mapping[i]=ri(26);
   for(int c:order){
    double bestdelta=std::numeric_limits<double>::infinity();int letter=0;
    if(r%4==2){letter=ri(26);}else for(int a=0;a<26;a++){
     double target=e.expected[a]*e.n;double old=e.lettercounts[a]-target;double delta=(2*old*e.counts[c]+double(e.counts[c])*e.counts[c])/(target+5);
     // Random perturbations diversify independent frequency starts.
     if(r>0)delta+=std::log(std::max(uni(),1e-12))*12.0;
     if(delta<bestdelta){bestdelta=delta;letter=a;}
    }
    e.mapping[c]=letter;e.lettercounts[letter]+=e.counts[c];
   }
  }
  double current_raw=e.score(),current=current_raw-freq_weight*e.penalty();
  if(current>best){best=current;best_raw=current_raw;best_map=e.mapping;}
  for(int it=0;it<steps;it++){
   std::vector<int> keys,old,next;int move=ri(100);
   if(move<65 || active.size()<2){int c=active[ri(active.size())];int a=ri(26);if(a==e.mapping[c])continue;keys={c};old={e.mapping[c]};next={a};}
   else if(move<95){int c=active[ri(active.size())],d=active[ri(active.size())];if(c==d||e.mapping[c]==e.mapping[d])continue;keys={c,d};old={e.mapping[c],e.mapping[d]};next={old[1],old[0]};}
   else {int a=ri(26),b=ri(26);if(a==b)continue;for(int c:active)if(e.mapping[c]==a||e.mapping[c]==b){keys.push_back(c);old.push_back(e.mapping[c]);next.push_back(e.mapping[c]==a?b:a);}if(keys.empty())continue;}
   auto affected=e.touched(keys);double before=0;for(int g:affected)before+=e.gram(g);
   double oldpen=e.penalty();
   for(int j=0;j<(int)keys.size();j++){int c=keys[j];e.mapping[c]=next[j];e.lettercounts[old[j]]-=e.counts[c];e.lettercounts[next[j]]+=e.counts[c];}
   double after=0;for(int g:affected)after+=e.gram(g);
   double rawdelta=after-before;double delta=rawdelta-freq_weight*(e.penalty()-oldpen);
   // Four fixed annealing cycles, each cooler than the previous cycle.
   int cycle=std::min(3,(int)(4LL*it/steps));double phase=double((4LL*it)%steps)/steps;
   double temp=std::max(0.04,max_temp*std::pow(0.55,cycle)*std::pow(0.004,phase));
   if(delta>=0 || uni()<std::exp(std::max(-700.0,delta/temp))){current+=delta;current_raw+=rawdelta;accepted++;if(current>best){best=current;best_raw=current_raw;best_map=e.mapping;}}
   else for(int j=0;j<(int)keys.size();j++){int c=keys[j];e.mapping[c]=old[j];e.lettercounts[next[j]]-=e.counts[c];e.lettercounts[old[j]]+=e.counts[c];}
  }
 }
 for(int i=0;i<k;i++)out[i]=best_map[i];e.mapping=best_map;e.recount();double full=e.score();stats[0]=full/e.total;stats[1]=full-freq_weight*e.penalty();stats[2]=accepted;stats[3]=std::abs(full-best_raw);stats[4]=e.total;return 0;
}
extern "C" double fh_delta(const int* data,const int* lengths,int books,int k,const double* table,const int* mapping,int c,int newletter){
 Engine e(data,lengths,books,k,table);for(int i=0;i<k;i++)e.mapping[i]=mapping[i];auto affected=e.touched({c});double before=0,after=0;for(int g:affected)before+=e.gram(g);e.mapping[c]=newletter;for(int g:affected)after+=e.gram(g);return after-before;
}

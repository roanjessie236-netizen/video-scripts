import json,re,sys
OUT=sys.argv[1] if len(sys.argv)>1 else 'lines.json'; OUTS=sys.argv[2] if len(sys.argv)>2 else 'subs.json'
def ts(s):
    h,m,r=s.split(':');a,b=r.split(',');return int(h)*3600+int(m)*60+int(a)+int(b)/1000
S={}
for b in open(sys.argv[3] if len(sys.argv)>3 else '../narration.srt',encoding='utf-8-sig').read().strip().split('\n\n'):
    l=b.strip().split('\n');a,z=l[1].split(' --> ');S[int(l[0])]=dict(s=ts(a),e=ts(z),zh=''.join(l[2:]))
EN={1:"Fire changed how we survive.",2:"Writing extended our memory.",3:"Machines amplified our strength.",
4:"And artificial intelligence is changing something deeper—",5:"Thinking.",6:"The machines of the past extended our hands.",
7:"Today's machines are starting to take part in creation, design and discovery.",8:"Abilities once thought to be uniquely human",
9:"are being re-examined.",10:"As intelligence leaves the lab and enters everyone's life,",11:"humanity's place is beginning to shift.",
12:"New jobs may emerge,",13:"while old skills may quickly lose their value.",
14:"Harari worries that some people may struggle for a long time to find a place in the economy",15:"— the risk of a \"useless class.\"",
16:"No longer being needed for work never means a person has lost their worth.",17:"Lifelong learning needs opportunity,",
18:"and the wealth technology creates must be shared.",19:"As work changes, how will we rethink our own worth?",
20:"If machines can write poetry,",21:"can paint,",22:"can even help us discover new knowledge,",23:"then is creativity still uniquely human?",
24:"Perhaps we need to rethink what creation means.",25:"A song can carry one person's longing.",26:"A painting can preserve the questions of an era.",
27:"Future creation will also happen between humans and new forms of intelligence.",28:"And we must still find what we truly want to express.",
29:"Artificial intelligence may change the world.",30:"But it cannot replace the questions humans ask.",31:"Why do we exist?",
32:"What kind of future do we want to create?",33:"As algorithms come to know us better and better,",34:"we, too, must come to know ourselves anew.",
35:"What do we truly long for?",36:"And for what kind of future are we willing to take responsibility?",37:"Our true advantage as humans",
38:"was never being faster than machines—",39:"it is having dreams,",40:"having love,",41:"having the power to choose the future.",
42:"The future is not yet written.",43:"Our choices are becoming history."}
# unit: (subs, rate, pitch, vol, cue)
U=[([1],-6,-2,0,'低沉、平静，开篇第一句'),([2],-6,-1,0,'与上句平行'),([3],-5,0,3,'排比第三句，略抬'),
([4],-4,-1,0,'转折，破折号处悬停'),([5],-8,-2,3,'单词落点，慢、重'),([6],-6,-1,0,'回望过去，平稳'),
([7],-5,1,3,'当下，三个动词递进'),([8,9],-5,0,0,'一口气说完，逗号处轻停'),([10,11],-6,-1,0,'叙述，后半句下沉'),
([12,13],-5,0,0,'对比：诞生 / 贬值'),([14,15],-4,0,0,'长句，破折号后点出“无用阶级”'),([16],-5,1,3,'坚定，强调“绝不”'),
([17,18],-5,0,3,'两个“需要”并列'),([19],-6,0,0,'设问，留白'),([20],-7,-1,0,'假设，轻起'),([21],-6,0,0,'短促递进'),
([22],-5,1,3,'递进到高点'),([23],-7,-1,0,'发问，放慢'),([24],-7,-1,0,'转入沉思'),([25],-7,-1,0,'温柔'),
([26],-7,0,0,'与上句平行'),([27],-4,1,0,'展望'),([28],-7,-2,3,'回到自身，沉稳'),([29],-5,0,0,'陈述'),
([30],-7,1,3,'转折，坚定'),([31],-8,-1,0,'根本之问，慢'),([32],-6,1,0,'第二问，向前'),([33,34],-6,-1,0,'对照：了解我们 / 认识自己'),
([35],-8,-1,0,'内省之问'),([36],-6,0,3,'责任，加重'),([37],-6,-1,0,'收束开始，沉'),([38],-7,0,0,'否定句'),
([39],-6,1,3,'“梦想”抬起'),([40],-8,0,3,'短，温暖'),([41],-6,1,5,'全片高点，坚定'),
([42],-15,-1,0,'片尾字幕：轻、慢、温柔'),([43],-15,-2,0,'片尾字幕：更轻，余韵')]
# burned subtitles cannot move: these two lines start a little earlier so they end with their subtitle
SHIFT={4:(11.25,'VO 提前 0.10 s（字幕后 0.05 s）以免超出烧录字幕'),27:(142.75,'VO 与字幕同时起（-0.05 s）以免超出烧录字幕')}
# #5: a 2-character standalone take came out creaky / mispronounced (Whisper: 「复刻」) -> synthesize it after the end of #4
CTX={5:('更深层的东西——','单独合成「思考。」两字时发音含混、偏沙哑（Whisper 识别为「复刻」）；改为与上句同语境「更深层的东西——思考。」一次合成，只保留「思考」')}
L=[]
for subs,r,p,v,c in U:
    i=subs[0]; cap=i>=42
    t=''.join(S[k]['zh'] for k in subs)
    L.append(dict(i=i,subs=subs,s=round(S[i]['s']+(0.6 if cap else 0.15),2),t=t,parts=[S[k]['zh'] for k in subs],
      en=' '.join(EN[k] for k in subs),rate=r,pitch='%+dHz'%p,vol='%+d%%'%v,cue=c,**({'cap':1} if cap else {})))
    if i in SHIFT: L[-1]['s'],L[-1]['note']=SHIFT[i]
    if i in CTX: L[-1]['ctx'],L[-1]['note']=CTX[i]
json.dump(L,open(OUT,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
json.dump({k:dict(S[k],en=EN[k]) for k in S},open(OUTS,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(L)); [print(x['i'],x['s'],x['t']) for x in L if len(x['subs'])>1]

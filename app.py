from flask import Flask, request, jsonify, render_template_string
import random
app=Flask(__name__)
SETS={
'1':['интеллигентность','ассимиляция','параллелепипед','аббревиатура','апеллировать','привередливый','комбинезон','периферия','бюллетень','целлофан'],
'2':['иррациональность','идентифицировать','коррозия','прецедент','палисадник','поскользнуться','привилегия','пессимистичный','прерогатива','брошюра']}
AUDIO_FILES={'интеллигентность': '01_интеллигентность.mp3', 'ассимиляция': '02_ассимиляция.mp3', 'параллелепипед': '03_параллелепипед.mp3', 'аббревиатура': '04_аббревиатура.mp3', 'апеллировать': '05_апеллировать.mp3', 'привередливый': '06_привередливый.mp3', 'комбинезон': '07_комбинезон.mp3', 'периферия': '08_периферия.mp3', 'бюллетень': '09_бюллетень.mp3', 'целлофан': '10_целлофан.mp3', 'иррациональность': '11_иррациональность.mp3', 'идентифицировать': '12_идентифицировать.mp3', 'коррозия': '13_коррозия.mp3', 'прецедент': '14_прецедент.mp3', 'палисадник': '15_палисадник.mp3', 'поскользнуться': '16_поскользнуться.mp3', 'привилегия': '17_привилегия.mp3', 'пессимистичный': '18_пессимистичный.mp3', 'прерогатива': '19_прерогатива.mp3', 'брошюра': '20_брошюра.mp3'}

S={'phase':'setup','names':[],'words':[],'wi':0,'pi':0,'typed':'','answers':{},'scores':{},'show_table':False}

def calc(a,b):
 a,b=a.lower(),b.lower(); n,m=len(a),len(b); d=[[0]*(m+1) for _ in range(n+1)]
 for i in range(n+1): d[i][0]=i
 for j in range(m+1): d[0][j]=j
 for i in range(1,n+1):
  for j in range(1,m+1): d[i][j]=min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(a[i-1]!=b[j-1]))
 i,j=n,m; ops=[]
 while i or j:
  if i and j and d[i][j]==d[i-1][j-1]+(a[i-1]!=b[j-1]): ops.append(['ok' if a[i-1]==b[j-1] else 'sub',a[i-1],b[j-1]]); i-=1;j-=1
  elif i and d[i][j]==d[i-1][j]+1: ops.append(['miss',a[i-1],'']); i-=1
  else: ops.append(['extra','',b[j-1]]); j-=1
 return d[n][m],list(reversed(ops))

STYLE='''<style>*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#351027,#080608 48%,#030303);color:#fff;font-family:Arial;min-height:100vh}.w{max-width:1150px;margin:auto;padding:28px}.logo{text-align:center;font-size:52px;font-weight:900;letter-spacing:6px;color:#ff59ba;text-shadow:0 0 22px #f08;margin-bottom:25px}.p{background:#0d0c0f;border:1px solid #63234b;border-radius:20px;padding:24px;margin:16px 0}.row{display:flex;gap:12px;flex-wrap:wrap}.lab{color:#a58d9b;font-size:13px;font-weight:900;letter-spacing:2px}input,select,button,a{background:#110b10;color:#fff;border:1px solid #773057;border-radius:13px;padding:14px 18px;font-size:17px}button,a{font-weight:900;cursor:pointer;text-decoration:none}.go{background:#ce197c}.pink{color:#ff5cba}.big{font-size:clamp(44px,7vw,92px);font-weight:900;text-align:center}.typed{font-size:clamp(44px,7vw,96px);font-weight:900;text-align:center;min-height:120px;word-break:break-all}.ans{font-size:clamp(20px,2.3vw,34px);font-weight:800;margin:14px 0}.bad{color:#ff506d;text-decoration:underline}.extra{color:#ff506d;text-decoration:line-through}.miss{color:#ffd057;border:1px dashed #ffd057;padding:0 4px}
@media (max-width:700px){
 body{padding:10px}.w{width:100%;max-width:none}.logo{font-size:42px;margin:12px 0 18px}
 .p{padding:18px;border-radius:18px}.p h2{font-size:24px}.lab{font-size:18px}.row{gap:10px}
 button,a,input,select{font-size:18px;min-height:52px}input{min-width:0;width:100%}
 .setbtn{flex:1;padding:14px 8px}.ans{font-size:20px}.typed{font-size:32px;padding:14px}
 #ctl button{width:100%;margin:5px 0}#ctl .row{display:block}
}
</style>'''

CONTROL='''<!doctype html><meta charset=utf-8>'''+STYLE+'''<div class=w><div class=logo>ДИКТАНТ</div><div class=p><h2>НАСТРОЙКА КОНКУРСА</h2>
<div class=lab style="margin-bottom:10px">НАБОР СЛОВ</div>
<div class=row><button id=set1 class="go setbtn" onclick="chooseSet(1)">НАБОР СЛОВ 1</button><button id=set2 class=setbtn onclick="chooseSet(2)">НАБОР СЛОВ 2</button></div>
<div class=lab style="margin-top:28px;margin-bottom:10px">КОЛИЧЕСТВО УЧАСТНИКОВ</div>
<div class=row style="align-items:center"><button onclick="changeCount(-1)" style="font-size:26px;width:58px">−</button><div id=countView style="font-size:32px;font-weight:900;min-width:55px;text-align:center;color:#ff5cba">4</div><button onclick="changeCount(1)" style="font-size:26px;width:58px">+</button></div>
<div class=lab style="margin-top:28px;margin-bottom:10px">УЧАСТНИКИ</div><div class=row id=names></div>
<div class=row style="margin-top:20px"><button class=go onclick=start()>НАЧАТЬ</button><a href=/screen target=_blank>ГОСТЕВОЙ ЭКРАН</a></div></div><div class=p id=ctl>ОЖИДАНИЕ</div><div class=p><button onclick=resetGame()>СБРОСИТЬ ИГРУ</button></div></div>
<script>
let ST={phase:'setup'};const $=x=>document.getElementById(x);let selectedSet='1',participantCount=4;
function chooseSet(n){selectedSet=String(n);$('set1').classList.toggle('go',n===1);$('set2').classList.toggle('go',n===2)}
function changeCount(d){participantCount=Math.max(1,Math.min(8,participantCount+d));$('countView').textContent=participantCount;mk()}
function mk(){let h='';for(let i=1;i<=participantCount;i++)h+=`<input id=n${i} value="УЧАСТНИК ${i}">`;names.innerHTML=h}mk();
async function start(){let a=[];for(let i=1;i<=participantCount;i++)a.push($('n'+i).value);await fetch('/api/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({set:selectedSet,names:a})});poll()}
async function resetGame(){await fetch('/api/reset',{method:'POST'});location.reload()} async function next(){await fetch('/api/next',{method:'POST'});poll()}
async function table(show){await fetch('/api/table',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({show:show})});poll()}
async function finishGame(){if(!confirm('Завершить конкурс и показать итоговые результаты?'))return;await fetch('/api/finish',{method:'POST'});poll()}
function playWord(){if(!ST.audio)return;new Audio(ST.audio).play().catch(()=>{})}
async function send(k){await fetch('/api/key',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:k})})}
document.addEventListener('keydown',e=>{if(ST.phase!=='typing')return;if(e.key==='Backspace'){e.preventDefault();send('BACKSPACE')}else if(e.key==='Enter'){e.preventDefault();send('ENTER')}else if(e.key.length===1&&/^[а-яА-ЯёЁ-]$/.test(e.key)){e.preventDefault();send(e.key)}});
async function poll(){ST=await(await fetch('/api/state?host=1')).json();if(ST.phase==='setup'){ctl.innerHTML='ОЖИДАНИЕ';return}let h=`<div class=lab>СЛОВО ${Math.min(ST.wi+1,10)} ИЗ 10</div>`;if(ST.phase==='typing')h+=`<div class=ans>Сейчас пишет: <span class=pink>${ST.name}</span></div><div class=ans>Правильное слово: <span class=pink>${ST.word}</span></div><button class=go onclick=playWord() style="width:100%;margin:10px 0 14px">🔊 ОЗВУЧИТЬ СЛОВО</button><div class=typed>${ST.typed||'_'}</div>`;if(ST.phase==='reveal')h+=`<div class=ans>Правильно: <span class=pink>${ST.word}</span></div><button class=go onclick=next()>СЛЕДУЮЩЕЕ СЛОВО</button>`;if(ST.phase==='finished')h='<div class="big pink">КОНКУРС ЗАВЕРШЁН</div>';if(ST.phase!=='finished'){h+=`<hr><div class=row><button class=go onclick="table(${!ST.show_table})">${ST.show_table?'ВЕРНУТЬСЯ К КОНКУРСУ':'ОТКРЫТЬ ТАБЛИЦУ'}</button><button onclick=finishGame()>ЗАВЕРШИТЬ КОНКУРС<br><span style="font-size:12px;font-weight:normal;color:#c9a9bb">с подсчётом результатов</span></button></div>`}h+='<hr><div class=lab>ОЧКИ</div>';for(const n of ST.names)h+=`<div class=ans>${n}: <span class=pink>${ST.scores[n]||0}</span></div>`;ctl.innerHTML=h}setInterval(poll,300);poll();
</script>'''

SCREEN='''<!doctype html><meta charset=utf-8>'''+STYLE+'''<div class=w><div class=logo>ДИКТАНТ</div><div class=p id=v style="min-height:650px"></div></div><script>
let ST={phase:'setup'};async function send(k){await fetch('/api/key',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:k})})}
document.addEventListener('keydown',e=>{if(ST.phase!=='typing')return;if(e.key==='Backspace'){e.preventDefault();send('BACKSPACE')}else if(e.key==='Enter'){e.preventDefault();send('ENTER')}else if(e.key.length===1&&/^[а-яА-ЯёЁ-]$/.test(e.key)){e.preventDefault();send(e.key)}});
function oh(o){return o.map(x=>x[0]==='ok'?x[2]:x[0]==='sub'?`<span class=bad>${x[2]}</span>`:x[0]==='extra'?`<span class=extra>${x[2]}</span>`:`<span class=miss>+${x[1]}</span>`).join('')}
function leaderboard(title){let h=`<div class="big pink">${title}</div><div class=lab style="text-align:center;margin:20px">МЕНЬШЕ ОШИБОК — ВЫШЕ МЕСТО</div>`;let rows=Object.entries(ST.scores).sort((a,b)=>a[1]-b[1]);for(let i=0;i<rows.length;i++){let [n,x]=rows[i];h+=`<div class=ans style="text-align:center">${i+1}. ${n} — <span class=pink>${x}</span> очк.</div>`}return h}
async function poll(){ST=await(await fetch('/api/state')).json();let h='';if(ST.phase==='setup')h='<div class=big>ОЖИДАНИЕ</div>';else if(ST.phase==='finished')h=leaderboard('ИТОГИ');else if(ST.show_table)h=leaderboard('ТАБЛИЦА ЛИДЕРОВ');else if(ST.phase==='typing')h=`<div class=lab style="text-align:center">СЛОВО ${ST.wi+1} ИЗ 10</div><div class="big pink" style="margin:25px">${ST.name}</div><div class=lab style="text-align:center">ВВОДИТЕ СЛОВО</div><div class=typed>${ST.typed||'_'}</div><div style="text-align:center;color:#a58d9b">BACKSPACE — ИСПРАВИТЬ &nbsp; ENTER — ПОДТВЕРДИТЬ</div>`;else if(ST.phase==='reveal'){h=`<div class=lab style="text-align:center">ПРАВИЛЬНЫЙ ОТВЕТ</div><div class="big pink">${ST.word}</div>`;for(const n of ST.names){let a=ST.answers[n];h+=`<div class=ans>${n}: ${oh(a.ops)} <span class=pink>— ${a.errors} очк.</span></div>`}}v.innerHTML=h}setInterval(poll,300);poll();
</script>'''

def snap(host=False):
 if S['phase']=='setup': return {'phase':'setup','names':[],'scores':{}}
 word=S['words'][S['wi']] if S['wi']<10 else ''
 name=S['names'][S['pi']] if S['phase']=='typing' else ''
 x={'phase':S['phase'],'names':S['names'],'scores':S['scores'],'wi':S['wi'],'name':name,'typed':S['typed'],'answers':S['answers'].get(str(S['wi']),{}),'show_table':S.get('show_table',False)}
 if host or S['phase'] in ('reveal','finished'):x['word']=word
 if host:x['audio']='/audio/'+AUDIO_FILES.get(word,'') if word else ''
 return x

@app.get('/')
def home():return render_template_string(CONTROL)
@app.get('/screen')
def screen():return render_template_string(SCREEN)
@app.get('/audio/<path:filename>')
def audio_file(filename):return send_from_directory('audio',filename)

@app.get('/api/state')
def state():return jsonify(snap(request.args.get('host')=='1'))
@app.post('/api/start')
def start():
 x=request.json or {}; names=x.get('names',[]); words=SETS[str(x.get('set','1'))][:];random.shuffle(words)
 S.clear();S.update(phase='typing',names=names,words=words,wi=0,pi=0,typed='',answers={},scores={n:0 for n in names},show_table=False);return jsonify(ok=True)
@app.post('/api/key')
def key():
 if S['phase']!='typing':return jsonify(ok=False),409
 k=str((request.json or {}).get('key',''))
 if k=='BACKSPACE':S['typed']=S['typed'][:-1]
 elif k=='ENTER':
  if not S['typed']:return jsonify(ok=False),400
  n=S['names'][S['pi']];e,o=calc(S['words'][S['wi']],S['typed']);S['answers'].setdefault(str(S['wi']),{})[n]={'errors':e,'ops':o};S['scores'][n]+=e;S['typed']='';S['pi']+=1
  if S['pi']>=len(S['names']):S['pi']=0;S['phase']='reveal'
 elif len(k)==1 and (k.isalpha() or k=='-') and len(S['typed'])<40:S['typed']+=k.lower()
 return jsonify(ok=True)
@app.post('/api/next')
def nxt():
 if S['phase']!='reveal':return jsonify(ok=False),409
 S['wi']+=1;S['phase']='finished' if S['wi']>=10 else 'typing';return jsonify(ok=True)
@app.post('/api/table')
def table():
 if S['phase'] in ('setup','finished'):return jsonify(ok=False),409
 S['show_table']=bool((request.json or {}).get('show',True));return jsonify(ok=True)

@app.post('/api/finish')
def finish():
 if S['phase']=='setup':return jsonify(ok=False),409
 S['typed']='';S['show_table']=False;S['phase']='finished';return jsonify(ok=True)

@app.post('/api/reset')
def reset():S.clear();S.update(phase='setup',names=[],words=[],wi=0,pi=0,typed='',answers={},scores={},show_table=False);return jsonify(ok=True)
if __name__=='__main__':app.run(host='0.0.0.0',port=5000,debug=True)

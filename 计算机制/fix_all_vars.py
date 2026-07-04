"""Add all missing global variables at the start of the first script"""
vault = r'C:\Users\苏砚仁\thinknote\南塘 DAO\gnt计算机制\工具\dashboard.html'
desktop = r'C:\Users\苏砚仁\Desktop\共创营工具\dashboard.html'

with open(vault, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the first <script> tag and inject ALL needed globals right after it
script_tag = '<script>'
idx = content.find(script_tag)
if idx < 0:
    print('No script tag')
    exit()

# All globals the code needs - declare them all upfront
globals_block = '''
// ── ALL GLOBAL STATE (injected to fix linter corruption) ──
var data = { tasks: [], decisions: [], members: {}, budget: {} };
var memberData = {};
var selectedMember = null;
var selectedPlayer = null;
var settleSelected = null;
var staffData = {};
var playerData = {};
var financeFilter = "全部";
var taskSortField = "";
var taskSortDir = 1;
var selectedPhase = "筹备期";
var currentScheduleView = "calendar";
var editingCalSlot = -1, editingCalDay = -1;
var editingAvatarStyle = 0;
var editingAvatarSeed = 0;
var mapSelectedPerson = null;
var mapSelectedGate = null;

function isStaff2(n) {
  var sn = ["砚仁","朝林","小红","若曦","淑惠","跳大爷"];
  return sn.some(function(s){return n.includes(s)});
}

var PIE_COLORS = ["#d4a853","#6b9b4e","#5b8cb8","#c47d5a","#8b6bae","#c4553d","#5fa89b","#d49b3d","#9b6b8e","#6b8e6b"];
var CHARACTER_SEEDS = ["Alex","Jordan","Casey","Morgan","Riley","Taylor","Quinn","Sam","Charlie","Drew","Blake","Avery","Skyler","Reese","Finley","Sage","Harper","Emery","Parker","Rowan","Dakota","Phoenix","River","Jamie","Kai","Sasha","Remy","Jules","Ari","Nico","Luca","Ezra","Theo","Ollie","Max","Leo","Mia","Zoe","Eli","Ivy","Asher","Nova","Kiran","Zuri"];
var AVATAR_STYLES = ["avataaars","adventurer","lorelei","open-peeps","notionists","personas","micah","bottts-neutral","fun-emoji","pixel-art","big-smile","thumbs"];
var ACHIEVEMENT_ICONS = {"课程":"🎨","宣传":"📢","生活":"🏠","财务":"💰","管理":"📋","结项":"📦","其他":"⭐"};
var MAP_MILESTONES = [
  {date:"06/06",name:"开营日",icon:"🏕️"},
  {date:"06/09",name:"动员会",icon:"📢"},
  {date:"06/22",name:"村展",icon:"🎨"},
  {date:"06/24",name:"城市展",icon:"🏙️"},
  {date:"06/26",name:"结项",icon:"🏁"}
];

function parseDate(s){if(!s)return Infinity;var m=s.match(/(\\d+)\\D+(\\d+)/);if(m)return new Date(2026,parseInt(m[1])-1,parseInt(m[2])).getTime();return Infinity}
function parseDateStr(s){if(!s)return Infinity;var m=s.match(/(\\d+)\\D+(\\d+)/);if(m)return new Date(2026,parseInt(m[1])-1,parseInt(m[2])).getTime();return Infinity}
function normalizeMD(s){if(!s)return"";var m=s.match(/(\\d+)\\D+(\\d+)/);if(m)return m[1].padStart(2,"0")+"/"+m[2].padStart(2,"0");return s}
function esc(s){return(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}
function escAttr(s){return(s||"").replace(/'/g,"\\\\'").replace(/"/g,"&quot;")}
function avatarUrl(idx,size){var seed=CHARACTER_SEEDS[idx]||"Alex";return"https://api.dicebear.com/9.x/avataaars/svg?seed="+seed+"&size="+(size||80)}
function avatarImg(idx,size){return\'<img src="\'+avatarUrl(idx,size)+\'" style="width:100%;height:100%;object-fit:cover" onerror="this.style.display=\\\'none\\\';var n=this.nextElementSibling;if(n)n.style.display=\\\'flex\\\'">\'}
function avatarInitial(idx){var c=["#d4a853","#6b9b4e","#5b8cb8","#c47d5a","#8b6bae"],s=CHARACTER_SEEDS[idx]||"?";return\'<span style="display:none;width:100%;height:100%;align-items:center;justify-content:center;font-size:1.2rem;font-weight:700;color:#fff;background:\'+c[idx%5]+\'">\'+esc(s[0])+\'</span>\'}
function avatarCircle(idx,size){return avatarImg(idx,size)+avatarInitial(idx)}
function classifyPhase(task){var n=(task.name||"")+(task.note||"")+(task.type||"");if(/改进|⚠️|缺失|没做|反思/.test(n))return"改进项";if(/结项|结算|复盘|报告|总结|工资条|财务结/.test(n))return"营后";if(/延期|变更|增时/.test(n))return"营后";if(/筹备|会前|开营前|预算|资助|提案|分工|认领|合伙人|里程碑|规则|合约|流程|动员会/.test(n))return"筹备期";return"营期"}
// ── END GLOBALS ──
'''

# Insert right after <script>
insert_pos = idx + len(script_tag)
content = content[:insert_pos] + globals_block + content[insert_pos:]

with open(desktop, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Done. Size: {len(content)} bytes')

import json, shutil
from pathlib import Path
import build_pdf as book

BASE=Path(__file__).resolve().parent.parent
DEST=BASE/'outputs'/'排序算法学习包'
DEST.mkdir(parents=True,exist_ok=True)
payload={'entries':book.ordered,'front':book.front,'groups':book.groups,'kinds':book.kindnames,'trees':book.tree_specs}
template=(Path(__file__).parent/'master_template.html').read_text()
encoded=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')
(DEST/'00_从这里开始.html').write_text(template.replace('__BOOK_DATA__',encoded))
animation=Path(__file__).parent/'animation_template.html'
if animation.exists():shutil.copy2(animation,DEST/'排序动画_从零开始.html')
assert len(book.ordered)==80
print('Master built:',DEST/'00_从这里开始.html')

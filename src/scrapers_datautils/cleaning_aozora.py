import re

def convert_tsv(save_path, book_text:str):
    book_text = remove_explanation(book_text)
    book_text = remove_ctrl_char(book_text)
    book_text = remove_ruby(book_text)

    # 最初と最後のブロックは本文じゃない
    blocks = book_text.split("\r\n\r\n")
    book_text = "\r\n".join(blocks[1:-1])

    text = []
    strs = book_text.split("\r\n")
    for s in strs:
        s = s.strip()
        sents = s.split("。")
        sents = [s for s in sents if len(s) > 2]
        text.extend(sents)

    with open(save_path, mode='w', encoding='utf-8', errors='ignore') as f:
        f.write("\t".join(text))

def remove_explanation(text:str):
    return re.sub(r"-+[^-]*-+", "", text)

def remove_ctrl_char(text:str):
    return re.sub(r"［＃.*］", "", text)

def remove_ruby(text:str):
    text = re.sub(r"\｜", "", text)
    return re.sub(r"《.+》", "", text)
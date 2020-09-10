import re

def convert_tsv(save_path:str, dialogue_dict:dict):
    save_lines = [l for d in dialogue_dict.values() if (l := dialogue_to_line(d))]
    save_lines = set(save_lines)
    save_lines = list(save_lines)

    with open(save_path, "w", encoding='utf-8', errors='ignore') as f:
        f.write('\n'.join(save_lines))

def dialogue_to_line(dialogue:dict) -> str:
    user_token = ["[ASC]", "[BSC]", "[CSC]", "[ZSC]"]
    lines = []
    user_dict = {}
    for tweet in dialogue:
        if tweet["user"] not in user_dict:
            user_dict[tweet["user"]] = len(user_dict)
        user_id = min(user_dict[tweet["user"]],3)
        lines.append(
            user_token[user_id]
            + remove_url(remove_name(tweet["text"])).replace("\n","__BR__")
        )

    if all(lines):
        return None

    return '\t'.join(lines)

def remove_name(tweet:str) -> str:
    return re.sub(r"@[0-9a-zA-Z_]{1,15} +", "", tweet)

def remove_url(tweet:str) -> str:
    return re.sub(r"https?://[\w!?/\+\-_~=;\.,*&@#$%\(\)\'\[\]]+", "", tweet)


if __name__ == "__main__":
    import sys
    import json
    args = sys.argv
    dialogue_dict = json.load(open(args[1], 'r'))
    convert_tsv(args[2], dialogue_dict)
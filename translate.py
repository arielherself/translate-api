import tiktoken
import openai
import local_secrets

openai.api_key = local_secrets.OPENAI_API_TOKEN
MODEL = 'text-davinci-003'
ALL_TOKEN = 4000 # do not make changes to this
MAX_TOKEN = 1000
PROMPT = 'Translate the article about $$$ below (before "ENDSIGNAL") into Chinese like human do:\n\n$$$$\n\nENDSIGNAL\n\nTranslation starts here:\n\n'
encoding = tiktoken.encoding_for_model(MODEL)
countToken = lambda s: len(encoding.encode(s))

def cut(s: str, mark: str=' ', verbosed=False) -> list[str]:
    print('Begin cutting...')
    w = list(s.split(mark))
    r = ['']
    currentIndex = 0
    listIndex = 0
    while len(w) > 0:
        t = ''
        if verbosed:
            print(f'[Step {len(r)}] Cutting the string...')
        for e in w:
            if countToken(t) > MAX_TOKEN:
                break
            else:
                t += ' ' + e
                listIndex += 1
        r[currentIndex] = t.lstrip()
        currentIndex += 1
        r.append('')
        w = w[listIndex:]
        listIndex = 0
    if verbosed:
        print('Finished cutting the string.')
    return list(filter(lambda s: s != '', r))

def translate(filename: str, subject: str, verbosed=False) -> str:
    source = open(filename, encoding='utf8').read()
    print('Begin translating...')
    result = []
    for i, each in enumerate(cut(source, verbosed=verbosed)):
        currentPrompt = PROMPT.replace('$$$$', each).replace('$$$', subject)
        if verbosed:
            print(f'[Step {i+1}] Requesting...')
        response = openai.Completion.create(model=MODEL, prompt=currentPrompt,  
                                            temperature=0.3, max_tokens=ALL_TOKEN-MAX_TOKEN, top_p=1.0,
                                            frequency_penalty=0.0, presence_penalty=0.0)
        result.append(response)
    if verbosed:
        print('Finished translating.')
    return '\n'.join([r['choices'][0]['text'] for r in result]).replace('ENDSIGNAL', '')
#!/usr/bin/python3

def get_frequencies():
    freqs = []
    with open('frequencies.csv', 'r') as inp:
        for idx, line in enumerate(inp):
            freqs.append(float(line.strip()))
    return freqs

class Generator(object):

    def __init__(self, steps, cents):
        self.lesson_id = None
        self.title = None
        self.lesson_heading = ""
        self.freqs = get_frequencies()
        self.cents = cents
        self.steps = steps

    def set_base(self, base):
        self.base = base
        assert self.base in self.freqs
        self.base_idx = self.freqs.index(self.base)
        self.target = self.freqs[self.base_idx + steps]
        self.target_idx = self.base_idx + steps

    def get_header(self):
        return """header {{
    lesson_id = "{lesson_id}"
    module = idbyname
    help = "idbyname-intonation"
    title = _("{title}")
    lesson_heading = _("{heading}")
    filldir = vertic
    }}
""".format(lesson_id=self.lesson_id, title=self.title, heading=self.title)

    def generate_question(self, first, second, name):
        return '''
question {{
     name = _i("{name}")
      set=0
       csound(load("share/sinus.orc"), """
   f1 0 4096 10 1 1.25 0.95 0.8 0.6 0.4 0.2 
   i1 0 1 {first:.6f}
   i1 + 1 {second:.6f}
 """)
 }}
'''.format(first=first, second=second, name=name)

    def generate_flat_question(self):
        name = "intonation|flat"
        second = self.target - (self.target - self.freqs[self.target_idx - 1]) / 100 * self.cents
        return self.generate_question(self.base, second, name)

    def generate_intune_question(self):
        name = "intonation|in tune"
        return self.generate_question(self.base, self.target, name)

    def generate_sharp_question(self):
        name = "intonation|sharp"
        second = self.target + (self.freqs[self.target_idx + 1] - self.target) / 100 * self.cents
        return self.generate_question(self.base, second, name)


freqs = get_frequencies()
for steps in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
    for cents in [10, 20, 30, 40, 50]:
        out_file = "intonation-%.2d_steps-%d_cents" % (steps, cents)
        gen = Generator(steps, cents)
        gen.lesson_id = "csound-intonation-%s_steps-%s_cents" % (steps, cents)
        gen.title = "Intonation: %d steps off by %d cents" % (steps, cents)
        out = gen.get_header()
        for freq in freqs[steps + 1 + 12:len(freqs)-steps-1 - 12]:
            gen.set_base(freq)
            out += gen.generate_flat_question()
            out += gen.generate_intune_question()
            out += gen.generate_sharp_question()
        with open(out_file, 'w') as outp:
            outp.write(out)

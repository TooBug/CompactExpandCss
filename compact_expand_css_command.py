import sublime
import sublime_plugin
import re


class CompactExpandCssCommand(sublime_plugin.TextCommand):
    def run(self, edit, action='compact'):
        # Format all the code
        if re.match(r'.*\.css$', self.view.file_name())  :
            regx = '\}[ \t]*(?=[^\n]\S)|\}\s+(?=\n)'
            rules1 = self.view.find_all(regx)
            for x in rules1:
                self.view.replace(edit, self.view.find(regx, x.a), "}\n")
        # Format all the code

        rule_starts = self.view.find_all('\{')
        rule_ends = self.view.find_all('\}')
        print (len(rule_starts) == len(rule_ends))
        print (rule_starts)
        print (rule_ends)
        if len(rule_starts) != len(rule_ends):
            sublime.message_dialog("value not match!")
            return

        tmp = Ele.getArea(rule_starts, rule_ends)


        rules_regions = list()
        regions_to_process = list()

        selections = self.view.sel()
        if len(selections) == 1 and selections[0].empty():
            selections = [sublime.Region(0, self.view.size())]

        # for i in range(len(rule_starts)):
        #     rule_region = sublime.Region(rule_starts[i].a, rule_ends[i].b)
        #     rules_regions.append(rule_region)
        #     for sel in selections:
        #         if sel.intersects(rule_region):
        #             regions_to_process.append(rule_region)
        #             break

        for i in range(len(tmp)):
            rule_region = tmp[i]
            rules_regions.append(rule_region)
            for sel in selections:
                if sel.intersects(rule_region):
                    regions_to_process.append(rule_region)
                    break





        regions_to_process.reverse()
        print("格式化序列: ", regions_to_process)
        self.process_rules_regions(regions_to_process, action, edit)

    def process_rules_regions(self, regions, action, edit):
        actions = {
            'compact': self.compact_rules,
            'expand': self.expand_rules,
            'toggle': self.toggle_rules
        }
        actions[action](regions, edit)

    def toggle_rules(self, regions, edit):
        grouped_rules = list()

        for r in regions:
            action_key = 'expand' if self.rule_is_compact(r) else 'compact'

            if not grouped_rules or not action_key in grouped_rules[-1]:
                grouped_rules.append({action_key: []})

            grouped_rules[-1][action_key].append(r)

        for group in grouped_rules:
            for (action, rules) in group.items():
                self.process_rules_regions(rules, action, edit)

    def compact_rules(self, regions, edit):
        view = self.view

        for collapse_region in regions:
            content = view.substr(collapse_region)

            if re.match(r"\{[^\}]*\{", content):
                continue

            match = re.match(r"\{([^\}]*)\}", content)

            rules = match.group(1).split(';')
            # rules = [r.strip() for r in rules]
            newRules = []
            for r in rules:
                key = r.strip()
                attr = key.split(':')
                attr = [a.strip() for a in attr]
                attr = ': '.join(attr)
                newRules.append(attr)
            rules = '; '.join(newRules)

            view.replace(edit, collapse_region, '{ ' + rules + '}')

    def expand_rules(self, regions, edit):
        view = self.view

        for expand_region in regions:
            content = view.substr(expand_region)

            print(expand_region.deep)

            if re.match(r"\{[^\}]*\{", content):
                continue

            if expand_region.deep > 0:
                indent = '\t'
            else:
                indent = ''

            match = re.match(r"\{([^\}]*)\}", content)

            rules = match.group(1).split(';')
            rules = filter(lambda r: r.strip(), rules)
            # rules = ['\t' + r.strip() + ';\n' for r in rules]
            newRules = []
            for r in rules:
                key = r.strip()
                attr = key.split(':')
                attr = [a.strip() for a in attr]
                attr = ': '.join(attr)
                newRules.append('\t' + indent + attr + ';\n')
            rules = ''.join(newRules)

            view.replace(edit, expand_region, '{\n' + rules + indent + '}')

    def rule_is_compact(self, rule):
        return re.match(r"^\{.*\}$", self.view.substr(rule))


def expand_to_css_rule(view, cur_point):
    '''expand cursor inside css rule to whole css rule'''
    rule = '^\w*[^{}\n]+ ?\{([^{}])*\}'
    css_rules = view.find_all(rule)
    for css_rule in css_rules:
        if css_rule.contains(cur_point):
            return css_rule
    # just return cur_point if not matching
    return cur_point


class ExpandToCssRuleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        regions = []

        for s in self.view.sel():
            regions.append(expand_to_css_rule(self.view, s))

        for r in regions:
            self.view.sel().add(r)


class Ele(sublime.Region):
    """css object"""
    deep = 0
    childEle = None
    # def __init__(self):
        # super(Ele, self).__init__()
        # self.arg = arg
        # print (rule_starts)
        # pass

    def getArea(rule_starts, rule_ends):
        length = len(rule_starts)
        area = list()
        childArea = list()
        pop = list()
        i = 0
        j = 0

        while j < length:

            r_end = rule_ends[j].b

            if i < length:
                l_start = rule_starts[i].a

                if l_start < r_end:
                    pop.append(l_start)
                    i = i + 1
                    # print("i: ", i)
                    continue
            t = Ele(pop.pop(), r_end)
            t.deep = len(pop)
            area.append(t)
            # print(Ele(pop.pop(), r_end))
            # pop.append(l_start)
            # i = i + 1
            j = j + 1
            # print("j: ", j)

        print("**构造序列: ", area)
        return area

        # print(pop)

        # for i in range(len(rule_starts)):
        #     l_start = rule_starts[i].a
        #     r_end = rule_ends[j].b

        #     # l_start_next = rule_starts[i+1].a

        #     # pop.append(l_start)
        #     if l_start < r_end:
        #         pop.append(l_start)
        #         # print (Ele(l_start_next, r_end))
        #     else:
        #         print(Ele(pop.pop(), r_end))
        #         pop.append(l_start)
        #         j = j + 1

        #     if i >= length - 1:
        #         break

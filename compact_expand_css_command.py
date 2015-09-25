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
        # Format all the code End

        rule_starts = self.view.find_all('\{')
        rule_ends = self.view.find_all('\}')

        if len(rule_starts) != len(rule_ends):
            sublime.message_dialog("value not match!")
            return

        area = Ele.getArea(rule_starts, rule_ends)

        rules_regions = list()
        regions_to_process = list()

        selections = self.view.sel()
        if len(selections) == 1 and selections[0].empty():
            selections = [sublime.Region(0, self.view.size())]

        for i in range(len(area)):
            rule_region = area[i]
            rules_regions.append(rule_region)
            for sel in selections:
                if sel.intersects(rule_region):
                    regions_to_process.append(rule_region)
                    break

        regions_to_process.reverse()
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
            
            tmpRules = []
            for r in rules:
                key = r.strip()
                attr = key.split(':')
                attr = [a.strip() for a in attr]
                attr = ': '.join(attr)
                tmpRules.append(attr)
            rules = '; '.join(tmpRules)

            view.replace(edit, collapse_region, '{ ' + rules + '}')

    def expand_rules(self, regions, edit):
        view = self.view

        for expand_region in regions:
            content = view.substr(expand_region)

            if re.match(r"\{[^\}]*\{", content):
                continue

            indent = ''
            if expand_region.deep > 0:
                indent = '\t'

            match = re.match(r"\{([^\}]*)\}", content)

            rules = match.group(1).split(';')
            rules = filter(lambda r: r.strip(), rules)
            
            tmpwRules = []
            for r in rules:
                key = r.strip()
                attr = key.split(':')
                attr = [a.strip() for a in attr]
                attr = ': '.join(attr)
                tmpwRules.append('\t' + indent + attr + ';\n')
            rules = ''.join(tmpwRules)

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
    """get regions"""
    deep = 0

    def getArea(rule_starts, rule_ends):
        length = len(rule_starts)
        area = list()
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
                    continue
            t = Ele(pop.pop(), r_end)
            t.deep = len(pop)
            area.append(t)
            j = j + 1

        return area

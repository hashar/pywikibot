#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This bot resets a (user) sandbox with predefined text.

This script understands the following command-line arguments:

&params;

Furthermore, the following command line parameters are supported:

    -hours:#       Use this parameter if to make the script repeat itself
                   after # hours. Hours can be defined as a decimal. 0.01
                   hours are 36 seconds; 0.1 are 6 minutes.

    -delay:#       Use this parameter for a wait time after the last edit
                   was made. If no parameter is given it takes it from
                   hours and limits it between 5 and 15 minutes.
                   The minimum delay time is 5 minutes.

    -text          The text that substitutes in the sandbox, you can use this
                   when you haven't configured clean_candbox for your wiki.

    -summary       Summary of the edit made by bot.

"""
#
# (C) Leonardo Gregianin, 2006
# (C) Wikipedian, 2006-2007
# (C) Andre Engels, 2007
# (C) Siebrand Mazeland, 2007
# (C) xqt, 2009-2018
# (C) Dr. Trigon, 2012
# (C) Pywikibot team, 2010-2018
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, division, unicode_literals

import datetime
import time

import pywikibot

from pywikibot import i18n, Bot, pagegenerators

content = {
    'commons': '{{Sandbox}}\n<!-- Please edit only below this line. -->',
    'wikidata': '{{Please leave this line alone (sandbox heading)}}',
    'wikivoyage': {
        'es': '<!--No borres este mensaje-->'
              '{{Zona de pruebas}}'
              '<!--Haz las pruebas debajo. Gracias-->\n\n'
              '== Las pruebas en esta sección ==\n',
    },
    'als': '{{subst:/Vorlage}}',
    'ar': '{{عنوان الملعب}}\n<!-- مرحبا! خذ راحتك في تجربة مهارتك في التنسيق '
          'والتحرير أسفل هذا السطر. هذه الصفحة لتجارب التعديل ، سيتم تفريغ '
          'هذه الصفحة كل 12 ساعة. -->',
    'arz': '{{عنوان السبوره}}\n<!-- مرحبا! خد راحتك فى تجريب مهاراتك فى\n'
           'التحرير تحت الخط ده. بما إن الصفحه دى لتجارب التعديل، فالصفحه دى '
           'حيتم تنضيفها\nاوتوماتيكيا كل 12 ساعه. -->',
    'az': '<!--- LÜTFƏN, BU SƏTRƏ TOXUNMAYIN --->\n{{Qaralama dəftəri}}\n'
          '<!-- AŞAĞIDAKI XƏTTİN ALTINDAN YAZA BİLƏRSİNİZ --->',
    'bar': '{{Bitte erst NACH dieser Zeile schreiben! (Begrüßungskasten)}}\n',
    'bn': '{{খেলাঘর}}<!-- অনুগ্রহপূর্বক এই লাইনটি অপসারণ করবেন না -->',
    'cs': '{{Tento řádek neměňte}}\n<!-- ************  Prosíme, '
          'NEMĚŇTE nic nad tímto řádkem.  Díky.  ************ -->\n\n'
          "== Bábovičky ==\n#'''první'''\n#''druhá''\n*třetí\n"
          "*'''''čtvrtá'''''\n pátá\n;šestá\n:sedmá",
    'da': '{{subst:Sandkasse tekst}}',
    'de': '{{subst:Wikipedia:Spielwiese/Vorlage}}',
    'en': '{{Sandbox heading}}\n<!-- Hello! Feel free to try your formatting '
          'and editing skills below this line. As this page is for editing '
          'experiments, this page will automatically be cleaned every 12 '
          'hours. -->',
    'eo': '{{Bonvolu ne forigi tiun ĉi linion (Provejo)}}',
    'fa': '{{subst:Wikipedia:ربات/sandbox}}',
    'fi': '{{subst:Hiekka}}',
    'fr': '{{subst:Préchargement pour Bac à sable}}',
    'he': '{{ארגז חול}}\n<!-- נא לערוך מתחת לשורה זו בלבד, תודה. -->',
    'hi': '{{User sandbox}}\n<!-- कृप्या इस लाइन के नीचे सम्पादन करे। -->',
    'id': '{{Bakpasir}}\n<!-- Uji coba dilakukan di baris di bawah ini -->',
    'it': '{{sandbox}}'
          '<!-- Scrivi SOTTO questa riga senza cancellarla. Grazie. -->',
    'ja': '{{subst:サンドボックス}}',
    'ko': '{{연습장 안내문}}',
    'ksh': '{{subst:/Schablon}}',
    'mzn': '{{ویکی‌پدیا:چنگ‌مویی صفحه/پیغوم}}\n<!-- سلام!اگه '
           'خواننی شه دچی‌ین مهارتون وسه تمرین هاکنین بتوننی اینتا صفحه جا '
           'ایستفاده هاکنین، اته لطف هاکنین اینتا پیغوم ره شه بقیه رفقون وسه '
           'بیلین. اینتا صفحه هرچند ساعت ربوت جا پاک بونه.-->',
    'my': '{{subst:Sandbox reset}}',
    'nds': '{{subst:/Vörlaag}}',
    'ne': '{{User sandbox}}\n'
          '<!-- कृप्या! यो लाइनको तल सम्पादन गर्नुहोला। -->',
    'nl': '{{subst:Wikipedia:Zandbak/schoon zand}}',
    'nn': '{{sandkasse}}\n<!-- Ver snill og IKKJE FJERN DENNE LINA OG LINA '
          'OVER ({{sandkasse}}) Nedanføre kan du derimot ha det artig og '
          'prøve deg fram! Lykke til! :-)  -->',
    'no': '{{Sandkasse}}\n<!-- VENNLIGST EKSPERIMENTER NEDENFOR DENNE '
          'SKJULTE TEKSTLINJEN! SANDKASSEMALEN {{Sandkasse}} SKAL IKKE '
          'FJERNES! -->}}',
    'pl': '{{Prosimy - NIE ZMIENIAJ, NIE KASUJ, NIE PRZENOŚ tej linijki '
          '- pisz niżej}}',
    'pt': '<!--não apague esta linha-->'
          '{{página de testes}}<!--não apagar-->\n',
    'ru': '{{/Пишите ниже}}\n'
          '<!-- Не удаляйте, пожалуйста, эту строку, тестируйте ниже -->',
    'simple': '{{subst:/Text}}',
    'sco': '{{subst:Saundbox}}',
    'shn': '{{subst:Sandbox reset}}',
    'sr': '{{песак}}\n'
          '<!-- Молимо, увежбавајте уређивање испод ове линије. Хвала. -->',
    'sv': '{{subst:Sandlådan}}',
    'th': '{{กระบะทราย}}\n<!-- กรุณาอย่าแก้ไขบรรทัดนี้ ขอบคุณครับ/ค่ะ -- '
          'Please leave this line as they are. Thank you! -->',
    'tr': '{{/Bu satırı değiştirmeden bırakın}}',
    'zh': '{{subst:User:Sz-iwbot/sandbox}}\n',
}

sandbox_titles = ('Q3938', 'Q28939665')

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp,
}


class SandboxBot(Bot):

    """Sandbox reset bot."""

    availableOptions = {
        'hours': 1,
        'no_repeat': True,
        'delay': None,
        'delay_td': None,
        'text': '',
        'summary': '',
    }

    def __init__(self, **kwargs):
        """Initializer."""
        super(SandboxBot, self).__init__(**kwargs)
        if self.getOption('delay') is None:
            d = min(15, max(5, int(self.getOption('hours') * 60)))
            self.availableOptions['delay_td'] = datetime.timedelta(minutes=d)
        else:
            d = max(5, self.getOption('delay'))
            self.availableOptions['delay_td'] = datetime.timedelta(minutes=d)

        self.site = pywikibot.Site()
        self.translated_content = self.getOption('text') or i18n.translate(
            self.site, content)
        if not self.translated_content:
            pywikibot.error('No content is given for pages, exiting.')
            raise RuntimeError
        if not self.generator:
            pages = []
            for item in sandbox_titles:
                p = self.site.page_from_repository(item)
                if p is not None:
                    pages.append(p)
            if not pages:
                pywikibot.bot.suggest_help(missing_generator=True)
                raise RuntimeError
            self.generator = pages

    def run(self):
        """Run bot."""
        self.site.login()
        while True:
            wait = False
            now = time.strftime('%d %b %Y %H:%M:%S (UTC)', time.gmtime())
            for sandbox_page in self.generator:
                pywikibot.output('Preparing to process sandbox page '
                                 + sandbox_page.title(as_link=True))
                if sandbox_page.isRedirectPage():
                    pywikibot.warning(
                        '{} is a redirect page, cleaning it anyway'
                        .format(sandbox_page.title(as_link=True)))
                try:
                    text = sandbox_page.text
                    if self.getOption('summary'):
                        translated_msg = self.getOption('summary')
                    else:
                        translated_msg = i18n.twtranslate(
                            self.site, 'clean_sandbox-cleaned')
                    subst = 'subst:' in self.translated_content
                    pos = text.find(self.translated_content.strip())
                    if text.strip() == self.translated_content.strip():
                        pywikibot.output(
                            'The sandbox is still clean, no change necessary.')
                    elif subst and sandbox_page.userName() == self.site.user():
                        pywikibot.output(
                            'The sandbox might be clean, no change necessary.')
                    elif pos != 0 and not subst:
                        sandbox_page.put(self.translated_content,
                                         translated_msg)
                        pywikibot.showDiff(text, self.translated_content)
                        pywikibot.output('Standard content was changed, '
                                         'sandbox cleaned.')
                    else:
                        edit_delta = (datetime.datetime.utcnow()
                                      - sandbox_page.editTime())
                        delta = self.getOption('delay_td') - edit_delta
                        # Is the last edit more than 'delay' minutes ago?
                        if delta <= datetime.timedelta(0):
                            sandbox_page.put(
                                self.translated_content, translated_msg)
                            pywikibot.showDiff(text, self.translated_content)
                            pywikibot.output('Standard content was changed, '
                                             'sandbox cleaned.')
                        else:  # wait for the rest
                            pywikibot.output(
                                'Sandbox edited {0:.1f} minutes ago...'
                                .format(edit_delta.seconds / 60.0))
                            pywikibot.output('Sleeping for {} minutes.'
                                             .format(delta.seconds // 60))
                            time.sleep(delta.seconds)
                            wait = True
                except pywikibot.EditConflict:
                    pywikibot.output(
                        '*** Loading again because of edit conflict.\n')
                except pywikibot.NoPage:
                    pywikibot.output(
                        '*** The sandbox is not existent, skipping.')
                    continue
            if self.getOption('no_repeat'):
                pywikibot.output('\nDone.')
                return
            elif not wait:
                if self.getOption('hours') < 1.0:
                    pywikibot.output('\nSleeping {} minutes, now {}'.format(
                        (self.getOption('hours') * 60), now))
                else:
                    pywikibot.output('\nSleeping {} hours, now {}'
                                     .format(self.getOption('hours'), now))
                time.sleep(self.getOption('hours') * 60 * 60)


def main(*args):
    """
    Process command line arguments and invoke bot.

    If args is an empty list, sys.argv is used.

    @param args: command line arguments
    @type args: unicode
    """
    opts = {}
    local_args = pywikibot.handle_args(args)
    gen_factory = pagegenerators.GeneratorFactory()
    for arg in local_args:
        if arg.startswith('-hours:'):
            opts['hours'] = float(arg[7:])
            opts['no_repeat'] = False
        elif arg.startswith('-delay:'):
            opts['delay'] = int(arg[7:])
        elif arg.startswith('-text'):
            if len(arg) == 5:
                opts['text'] = pywikibot.input(
                    'What text do you want to substitute?')
            else:
                opts['text'] = arg[6:]
        elif arg.startswith('-summary'):
            if len(arg) == len('-summary'):
                opts['summary'] = pywikibot.input('Enter the summary:')
            else:
                opts['summary'] = arg[9:]
        else:
            gen_factory.handleArg(arg)

    generator = gen_factory.getCombinedGenerator()

    bot = SandboxBot(generator=generator, **opts)
    bot.run()


if __name__ == '__main__':
    main()

import os

class Settings(object):
    ''' Handles settings for skt-chat client and server.

    Reads settings from a config file line by line.  Settings are stored in the
    files as 'setting:value' strings.
    '''
    def __init__(self, setting_type):
        types = ['server', 'client']
        if setting_type not in types:
            raise ValueError('Settings setting_type must be \'server\' or \'client\'')

        self.setting_type = setting_type

        self.settings = {}

        self.readConfig()

    def readConfig(self):
        ''' Read config file in to self.settings '''
        settings_filename = 'settings.%s' % self.setting_type

        if not os.path.isfile(settings_filename):
            return

        with open('settings.client', 'r') as settings_file:
            lines = settings_file.readlines()

        for i, curline in enumerate(lines):
            curline = curline.strip().split(':')
            try:
                self.settings[curline[0]] = curline[1]
            except IndexError:
                print('Invalid line in configuration file: %d: "%s"'%(i,''.join(curline)))


    def editSetting(self, setting, value):
        ''' Edit a single setting in the config file and update settings_dict

        Args:
        setting: name of setting, string
        value: value of setting, string
        '''
        settings_filename = 'settings.%s' % self.setting_type
        # Is set to True if setting is found in file
        setting_match = False

        if not os.path.isfile(settings_filename):
            temp = open(settings_filename, 'w+')
            temp.close()
            lines = []
        else:
            with open(settings_filename, 'r') as settings_file:
                lines = settings_file.readlines()

            # Update setting line
            for i, line in enumerate(lines):
                if line.startswith('%s:' % setting):
                    setting_match = True
                    new_line = '%s:%s\n'%(setting,value)
                    lines[i] = new_line
                    break

        # Setting didn't exist in file, create it
        if not setting_match:
            lines.append('%s:%s\n'%(setting, value))

        self.settings[setting] = value

        with open(settings_filename, 'w') as settings_file:
            settings_file.writelines(lines)

    def getSetting(self, setting):
        '''
        Args:
        setting: name of setting, string
        '''
        if setting in self.settings.keys():
            return self.settings[setting]
        else:
            return False

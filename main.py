from lxml import etree, objectify


def parse_xml(xml_file):    
    with open(xml_file) as f:
        xml = f.read()

    xml = xml[3::].encode('utf-8')
    root = etree.fromstring(xml)
    for child in root.getchildren():
        for element in child.getchildren():
            print(element.attrib)

if __name__ == '__main__':
    parse_xml('oval\oval_com.altx-soft.win_def_81925.xml')


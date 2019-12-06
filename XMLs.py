# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 21:05:02 2016

@author: netzer

This .py file is a module for the operations1 project and only contains
XML-templates used in various scripts of that project. For security reasons the
contents of the templates was left blank.
"""

deactivate = '''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<data>
  <header>
...
  </header>
       <transactions>                                

       </transactions>
</data>
'''

tectraxx_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Response Konfektionierung Partner -->
<data xsi:noNamespaceSchemaLocation="pd_imp.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<header>
	...
	</header>
	<packing_units>
 
	</packing_units>
</data>'''.encode('utf-8')


rrem_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Response Konfektionierung Partner -->
<data xsi:noNamespaceSchemaLocation="pd_imp.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<header>
		...
	</header>
	<packing_units>

	</packing_units>
</data>
'''.encode('utf-8')

codes_import_xml = '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<data xmlns:xsi="http://www.w3.org/2001/XMLSchema">
	<header>
		...
	</header>
	<cards>

	</cards>
</data>'''.encode('utf-8')

tx_solds = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<data>
	<header>
		...
	</header>
	<transactions>
		
 
 	</transactions>
      </data>'''.encode('utf-8')

card_import_xml = '''<?xml version="1.0" encoding="utf-8"?>
<data>
  <header>
    ...
  </header>
  <cards>
  </cards>
</data>'''.encode('utf-8')
# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_get__json 1"] = b'"value"'

snapshots[
    "test_get__partial_template 1"
] = """





    
        <div id="component-component_2-inner" class="dashboard-component-inner fade-in">
            
value

        </div>
    





"""

snapshots[
    "test_model_dashboard__object_is_set 1"
] = """





    
        <div id="component-component_1-inner" class="dashboard-component-inner fade-in">
            
value

        </div>
    





"""
import os
import tempfile
import sys
sys.path.insert(0, os.path.dirname(__file__))
import local_peer

with tempfile.TemporaryDirectory() as d:
    local_peer.ROOT = __import__('pathlib').Path(d)
    local_peer.DB = local_peer.ROOT / 'peer.db'
    local_peer.enqueue('t1', 'missing', {'x': 1})
    assert not local_peer.admit('t1')
    assert local_peer.connect().execute("select state from jobs where job_id='t1'").fetchone()[0] == 'REJECTED'
print('local peer tests passed')

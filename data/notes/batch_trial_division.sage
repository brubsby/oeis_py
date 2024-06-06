def product(X):
  if len(X) == 0: return 1
  while len(X) > 1:
    X = [prod(X[i*2:(i+1)*2]) for i in range((len(X)+1)//2)]
  return X[0]

def producttree(X):
  result = [X]
  while len(X) > 1:
    X = [prod(X[i*2:(i+1)*2]) for i in range((len(X)+1)//2)]
    result.append(X)
  return result

def remaindersusingproducttree(n,T):
  result = [n]
  for t in reversed(T):
    result = [result[floor(i/2)] % t[i] for i in range(len(t))]
  return result

def remainders(n,X):
  return remaindersusingproducttree(n,producttree(X))

def primesin(P,x):
  result = remainders(x,P)
  return [p for p,r in zip(P,result) if r == 0]

def primesinproduct(P,X):
  return primesin(P,product(X))

def primesineach(P,X):
  n = len(X)
  if n == 0: return []
  P = primesinproduct(P,X)
  if n == 1: return [P]
  return primesineach(P,X[:n//2]) + primesineach(P,X[n//2:])

P = list(primes(2,10))
X = [50,157,266,377,490,605]
print(primesineach(P,X))
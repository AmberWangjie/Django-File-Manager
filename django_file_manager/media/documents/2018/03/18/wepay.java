public class Tuple{
	public long a;
	public long b;
	public long pow;
	public Tuple(int a, int b, int p){
		this.a = a;
		this.b = b;
		this.pow = p;
	}
}

public class PowerNumbers{
	public long getPowerNumber(long index){
		if(index < 0L){
			//err input
			return -1;
		}
		Queue<Tuple> minHeap = new PriorityQueue<>((int)(index + 1), new Comparator<Tuple>(){
			public int compare(Tuple t1, Tuple t2){
				t1.pow = math.pow(t1.a, t1.b);
				t2.pow = math.pow(t2.a, t2.b);
				if(t1.pow == t2.pow){
					return t1.a < t2.a ? -1 : 1;
				}
				return t1.pow < t2.pow ? -1 : 1;
			}
		});
		Set<Long> visit = new HashSet<>();
		Tuple curr = new Tuple(2L, 2L, (long)(math.pow(2, 2)));
		minHeap.offer(curr);
		long res = 0L;
		while(!minHeap.isEmpty()){
			curr = minHeap.poll();
			visit.add(curr.pow);
			if(visit.size() == index + 1){
				res = curr.pow;
				break;
			}
			Tuple newT = new Tuple(curr.a + 1, curr.b);
			minHeap.offer(newT);
			newT = new Tuple(curr.a, curr.b + 1);
			minHeap.offer(newT);
		}
		return res;
	}
}
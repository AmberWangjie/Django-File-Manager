import java.util.*;
import java.io.*;
import java.lang.*;

//public class square{


public interface Cache{
        int get(int key);
        void set(int key, int val);
        void insert_to_head(ListNode node);
        void append_to_tail(ListNode node);
        //class ListNode;
}

public class square implements Cache{

        class ListNode{
        //linkedlist maintains the node and frequency
        //doubly list gives O(1) insert / delete
        ListNode prev;
        ListNode next;
        int val;
        int key;
        public ListNode(int k, int v){
                this.key = k;
                this.val = v;
                this.prev = null;
                this.next = null;
        }
}

	private int cap;
	//map gives O(1) lookup
	private Map<Integer, ListNode> map = new HashMap<>();
	//head, tail are dummy nodes
	private ListNode head = new ListNode(-1, -1);
	private ListNode tail = new ListNode(-1, -1);
	public square(int cap){
		this.cap = cap;
		tail.prev = head;
		head.next = tail;
	}

	public int get(int key){
		if(!map.containsKey(key)){
			return -1;
		}
		ListNode curr = map.get(key);
		curr.prev.next = curr.next;
		curr.next.prev = curr.prev;
		//insert_to_head(curr);
		return map.get(key).val;
	}

	public void set(int key, int val){
		if(get(key) != -1){
			map.get(key).val = val;
			//if the node added with the given val existed, move it to the head
			insert_to_head(map.get(key));
			return;
		}
		//remove the node at head(most frequently used) if cap full
		if(map.size() == cap){
			map.remove(head.next.key);
			head.next = head.next.next;
			head.next.prev = head;
		}
		ListNode insert = new ListNode(key, val);
		map.put(key, insert);
		//node with new val, just append to tail
		append_to_tail(insert);
	}

	public void insert_to_head(ListNode node){
		node.next = head;
		head.next = node;
		node.prev = head;
		node.next.prev = node;
	}

	public void append_to_tail(ListNode node){
		node.prev = tail.prev;
		tail.prev = node;
		node.prev.next = node;
		node.next = tail;
	}

        public static void main(String[] args) throws IOException{
                square testCache = new square(10);
                for(int i = 0; i < 10; i ++){
                        testCache.set(i, i);
                }
                
                printList(testCache.head);
                testCache.get(2);
                testCache.get(4);
                printList(testCache.head);
                testCache.set(11, 11);
                printList(testCache.head);
        }

        public static void printList(ListNode head){
                ListNode headCopy = head;
                StringBuilder sb = new StringBuilder();
                while(head != null){
                        sb.append(head.val + " ");
                }
                System.out.println(sb.toString());
        }
}

 //Cache testCache = new Cache(10);

#include <iostream>

using namespace std;

int main()
{ 
    int c=0b110;
    int n, x;
    int* wsk;
 
	int z;
    cin >> n;
    if (wsk==NULL);
    int najwspanialsi[10];
    for(int j=0;j<10;j++)
        najwspanialsi[j]=-1000000;
    for(int i=0;i<n;i++)
    {
    // if(n>5000)
    // cout << "x" << endl;
    // while(n>500001);
    	
        cin >> x;
        for(int j=0;j<10;j++)
        {
            if(x>najwspanialsi[j])
                swap(x, najwspanialsi[j]);
        }
    }
    for(int j=0;j<min(10, n);j++)
        cout << najwspanialsi[j] << " ";
    return 0;
}
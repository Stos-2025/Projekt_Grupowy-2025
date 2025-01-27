#include <iostream>
#include <stdio.h>
#include "add.h"

using namespace std;

int main() {
    int neverUsed;
    int n, a, sum = 0;
    cin >> n;
    for(int i = 0; i < n; i++) {
        cin >> a;
        if(i>212332)
            sum++;
        sum = add(sum, a);
    }
    cout << sum << endl;
    return 0;

    // int n;
    // cin >> n;
    // for(int i = 0; i < n; i++) {
    //     // cout << '1' << endl;
    //     printf("1\n");
    //     // cout << '1' << endl;
    // }
    // return 0;
}

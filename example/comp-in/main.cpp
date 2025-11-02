#include <iostream>
#include <stdio.h>
#include "add.h"

using namespace std;


void sum(int n){
    int a, tsum = 0;
    // for(int i = 0; i < n; i++);
    for(int i = 0; i < n; i++) {
        cin >> a;
        tsum +=a;
    }
    cout << tsum << endl;
}

int main() {
    int neverUsed;
    int n;
    cin >> n;
    for (int i = 0; i < n/5; ++i) {
        void* ptr = malloc(1024 * 1024 * 20); // 10MB na iterację
        if (!ptr) break;
        memset(ptr, i, 1024 * 1024 * 20);
        std::cerr << "Allocated " << (i + 1) * 10 << " MB" << std::endl;
    }
    sum(n);
    // cin >> neverUsed;
    return 0;
}

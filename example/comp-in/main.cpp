#include <iostream>
#include <stdio.h>
#include "add.h"

using namespace std;


void sum(){
    int n, a, sum = 0;
    cin >> n;
    for(int i = 0; i < n; i++) {
        cin >> a;
        sum +=a;
    }
    cout << sum << endl;
}

int main() {
    int neverUsed;
    for (int i = 0; i < 1000; ++i) {
        void* ptr = malloc(1024 * 1024 * 10); // 10MB na iterację
        if (!ptr) break;
        memset(ptr, i, 1024 * 1024 * 10);
        std::cerr << "Allocated " << (i + 1) * 10 << " MB" << std::endl;
    }
    sum();
    return 0;
}

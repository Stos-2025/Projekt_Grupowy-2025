use std::io;

fn main() {
    let mut input = String::new();
    io::stdin().read_line(&mut input);
    let n: usize = input.trim().parse().expect("Invalid input");

	let mut sum: i32 = 0;
    for i in 1..=n {
        input.clear();
        io::stdin().read_line(&mut input);
        let number: i32 = input.trim().parse().expect("Invalid input");
        sum += number;
    }
    println!("{}", sum);
}

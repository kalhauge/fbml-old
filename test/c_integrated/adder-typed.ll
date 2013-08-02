; ModuleID = 'main'

define void @multi_add(i32 %a, i32 %b, i32 %c, i32 %d, i32* %e) {
entry:
  %n2 = add i32 %c, %d
  %n1 = add i32 %a, %b
  %e1 = add i32 %n1, %n2
  store i32 %e1, i32* %e
  ret void
}

define void @multiply_with_four(i32 %a, i32* %b) {
entry:
  call void @multi_add(i32 %a, i32 %a, i32 %a, i32 %a, i32* %b)
  ret void
}

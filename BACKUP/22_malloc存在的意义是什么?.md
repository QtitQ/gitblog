# [malloc存在的意义是什么?](https://github.com/chaleaoch/gitblog/issues/22)


Table of Contents
=================



\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
栈上变量的大小是在**编译期**确定的. 

如果需要动态分配内存 (例如编译期大小不能确定的变量), 或者希望自己控制变量的生命周期, 则需要将变量分配到堆内存上. 堆内存分配就要使用malloc.

像Java, Python这种语言, 会由其runtime决定变量分配到栈内存还是堆内存, 不是不需要, 只是没有暴露给用户而已.
int main(void)
{		
	Init_HX711pin();
	delay_init();
	
	NVIC_Configuration(); 	 //设置NVIC中断分组2:2位抢占优先级，2位响应优先级
	uart_init(9600);	 //串口初始化为9600
	
	while(1)
	{
		Get_Weight();

		printf("weight=%dg\r\n",Weight_Shiwu); //打印 
		delay_ms(200);

	}
}



long HX711_Read(void)	//增益128
{
	//unsigned long count; 
	long count; 
	unsigned char i; 
  	HX711_DOUT=1; 
	delay_us(1);
  	HX711_SCK=0; 
  	count=0; 
  	while(HX711_DOUT); 
  	for(i=0;i<24;i++)
	{ 
	  	HX711_SCK=1; 
	  	count=count<<1; 
		delay_us(1);
		HX711_SCK=0; 
	  	if(HX711_DOUT)
			count++; 
		delay_us(1);
	} 
 	HX711_SCK=1; 
    count=count^0x800000;//第25个脉冲下降沿来时，转换数据
	delay_us(1);
	HX711_SCK=0;  
	return(count);
}

//打表
int32_t weights[] = {
    18000, 18500, 19000, 19500, 20000, 20500, 21000, 21500, 22000, 22500,
    23000, 23500, 24000, 24500, 25000, 25500, 26000, 26500, 27000, 27500, 28000
};

// 手动记录的HX711读数
int32_t hx711_readings[] = {
    7758780, 7963332, 8167884, 8372436, 8576988, 8781540, 8986092, 9190644, 9395196, 9599748,
    9804300, 10008852, 10213404, 10417956, 10622508, 10827060, 11031612, 11236164, 11440716, 11645268, 11849820
};
int table_size = 21; // 表的大小

void Get_Weight(void)
{
	HX711_Buffer = HX711_Read();
	Weight_Shiwu = get_weight(HX711_Buffer);

}

// 线性插值函数，返回 int32_t 类型
int32_t linear_interpolation(int32_t x, int32_t x0, int32_t x1, int32_t y0, int32_t y1) {
    return y0 + (int32_t)((y1 - y0) * (x - x0) / (x1 - x0));
}
int i;
// 通过读数获取重量的打表函数，返回 int32_t 类型
int32_t get_weight(int32_t hx711_output) {
    // 处理表外的情况
    if (hx711_output <= hx711_readings[0]) return (int32_t)((float)hx711_output/GapValue);
    if (hx711_output >= hx711_readings[table_size - 1]) return (int32_t)((float)hx711_output/GapValue);

    // 在表中查找合适的两个点进行插值
		//int16_t i = 0;
    for (i = 0; i < table_size - 1; i++) {
        if (hx711_output < hx711_readings[i + 1]) {
            return linear_interpolation(hx711_output, hx711_readings[i], hx711_readings[i + 1], weights[i], weights[i + 1]);
        }
    }

    // 如果所有的比较都不符合，返回最大重量（理论上不会发生）
    return weights[table_size - 1];
}

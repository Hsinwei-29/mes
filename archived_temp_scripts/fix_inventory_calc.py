import re

# 讀取檔案
with open(r'd:\app\mes\app\models\inventory.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到需要替換的部分
old_pattern = r"""                # 取得成品欄位索引
                config = CONFIGS\.get\(part_name, \[\]\)
                finished_col_idx = None
                for label, idx in config:
                    if label in \['成品', '成品研磨'\]:
                        finished_col_idx = idx
                        break
                
                # 初始化該料件的總數
                part_total = 0

                # 提取機型詳細資料並累加總數
                if '機型' in df\.columns:
                    for _, row in df\.iterrows\(\):
                        model = row\.get\('機型', ''\)
                        # 排除無效機型
                        if pd\.notna\(model\) and str\(model\)\.strip\(\) and str\(model\)\.strip\(\) != '品號':
                            model_str = str\(model\)\.strip\(\)
                            
                            # 初始化該機型的數據
                            if model_str not in all_models:
                                all_models\[model_str\] = \{'機型': model_str, '工作台': 0, '底座': 0, '橫樑': 0, '立柱': 0\}
                            
                            # 取得成品數量
                            finished_value = 0
                            if finished_col_idx is not None:
                                val = row\.iloc\[finished_col_idx\]
                                if pd\.notna\(val\):
                                    try:
                                        finished_value = int\(float\(val\)\)
                                    except:
                                        finished_value = 0
                            
                            # 累加到總表 \(使用 \+= 處理重複出現的機型\)
                            all_models\[model_str\]\[part_name\] \+= finished_value
                            
                            # 累加到該料件總數
                            part_total \+= finished_value"""

new_code = """                # 取得所有製程欄位的索引（排除總數欄位）
                config = CONFIGS.get(part_name, [])
                process_col_indices = [idx for label, idx in config if label != '總數']
                
                # 初始化該料件的總數
                part_total = 0

                # 提取機型詳細資料並累加總數
                if '機型' in df.columns:
                    for _, row in df.iterrows():
                        model = row.get('機型', '')
                        # 排除無效機型
                        if pd.notna(model) and str(model).strip() and str(model).strip() != '品號':
                            model_str = str(model).strip()
                            
                            # 初始化該機型的數據
                            if model_str not in all_models:
                                all_models[model_str] = {'機型': model_str, '工作台': 0, '底座': 0, '橫樑': 0, '立柱': 0}
                            
                            # 加總所有製程欄位的數量
                            row_total = 0
                            for col_idx in process_col_indices:
                                if col_idx < len(row):
                                    val = row.iloc[col_idx]
                                    if pd.notna(val):
                                        try:
                                            row_total += int(float(val))
                                        except:
                                            pass
                            
                            # 累加到總表 (使用 += 處理重複出現的機型)
                            all_models[model_str][part_name] += row_total
                            
                            # 累加到該料件總數
                            part_total += row_total"""

# 替換
content = re.sub(old_pattern, new_code, content)

# 寫回檔案
with open(r'd:\app\mes\app\models\inventory.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("修改完成！")

# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QApplication,QVBoxLayout,QSpacerItem,QSizePolicy
from PySide6.QtGui import QIcon, QFont
from qfluentwidgets import LineEdit, PushButton,ComboBox,InfoBar,InfoBarPosition,ToolTipFilter,ToolTipPosition
from PySide6.QtWidgets import QWidget,QHBoxLayout
from PySide6.QtCore import Qt, QThread, Signal
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
import joblib
import os
import pandas as pd
from scipy.stats import zscore
import time

# 设置中文字体和负号显示
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# 获取当前脚本目录的函数
def get_current_directory():
    current_file_path = os.path.abspath(__file__)
    return os.path.dirname(current_file_path)


# 模型训练线程
class TrainModelsThread(QThread):
    progress_signal = Signal(int)  # 信号：用于更新进度条
    finished_signal = Signal()  # 信号：表示线程完成

    def __init__(self, data_processed, model_type):
        super().__init__()
        self.data_processed = data_processed
        self.model_type = model_type  # 模型类型
        self._is_running = True  # 标志位：控制线程是否继续运行

    def run(self):
        # 定义保存模型的文件夹为当前工作目录下的 "models"
        model_dir = os.path.join(os.path.dirname(get_current_directory()), "models")
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        # 获取所有作物种类
        crop_types = self.data_processed['作物种类'].unique()
        total_crops = len(crop_types)

        for idx, crop_type in enumerate(crop_types):
            if not self._is_running:  # 检查线程是否需要停止
                break

            model_filename = os.path.join(model_dir, f"{self.model_type}_model_crop_{crop_type}.pkl")
            if not os.path.exists(model_filename):  # 仅训练未保存的模型
                crop_data = self.data_processed[self.data_processed['作物种类'] == crop_type]
                X_crop = crop_data[['降雨量', '气温', 'ph值']]
                y_crop = crop_data['产量']

                # 创建模型
                model = self.get_model()
                model.fit(X_crop, y_crop)

                # 保存模型
                joblib.dump(model, model_filename)

            # 更新进度信号
            self.progress_signal.emit(int((idx + 1) / total_crops * 100))
            time.sleep(0.01)  # 模拟训练时间延迟

        self.finished_signal.emit()  # 发出完成信号

    def get_model(self):
        """根据用户选择返回相应的回归模型"""
        if self.model_type == "RandomForest":
            return RandomForestRegressor(n_estimators=100, random_state=42)
        elif self.model_type == "DecisionTree":
            return DecisionTreeRegressor(random_state=42)
        elif self.model_type == "DecisionTreeOptimized":
            # 使用之前优化得到的最佳超参数
            best_params_cart = [20, 3, 1]  # 从粒子群优化得到的最佳超参数
            return DecisionTreeRegressor(max_depth=best_params_cart[0], 
                                              min_samples_split=best_params_cart[1], 
                                              min_samples_leaf=best_params_cart[2], 
                                              random_state=42)
        elif self.model_type == "XGBoost":
            return XGBRegressor(objective="reg:squarederror", random_state=42)
        elif self.model_type == "XGBoostOptimized":
            # 优化后的XGBoost超参数
            best_params_xgb = [200, 10, 2, 0.09713775005616568] 
            return XGBRegressor(n_estimators=int(best_params_xgb[0]),
                                max_depth=int(best_params_xgb[1]),
                                learning_rate=best_params_xgb[3],
                                random_state=42)
        else:
            raise ValueError(f"未知的模型类型: {self.model_type}")

    def stop(self):
        """停止线程"""
        self._is_running = False


# 主窗口类
class Ui_predictpage(object):
    def setupUi(self, PredictPage):
        PredictPage.setObjectName("predictpage")

        
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_data()
        self.train_thread = None  # 初始化线程变量
        self.contents = [
            "你好",
            "在点击试试",
            "在点击一次",
            "你干嘛,诶呦",
            "别点了",
            "666"
        ]
        self.current_index = 0  # 当前索引

    from PySide6.QtWidgets import QSpacerItem, QSizePolicy

    def initUI(self):
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.setWindowTitle('作物产量预测系统')

        # 主布局：外层垂直布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)  # 设置控件间距

        # 添加顶部伸展，使控件整体居中
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 内容布局：垂直布局
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(30)
        self.content_layout.setAlignment(Qt.AlignCenter)  # 内容居中对齐

        # 创建输入框和标签
        self.rainfall_input = LineEdit(self)
        self.rainfall_input.setPlaceholderText('请输入降雨量 (mm)')
        self.rainfall_input.setMaximumWidth(350)
        self.content_layout.addWidget(self.rainfall_input)

        self.temperature_input = LineEdit(self)
        self.temperature_input.setPlaceholderText('请输入气温 (°C)')
        self.temperature_input.setMaximumWidth(350)
        self.content_layout.addWidget(self.temperature_input)

        self.ph_input = LineEdit(self)
        self.ph_input.setPlaceholderText('请输入pH值')
        self.ph_input.setMaximumWidth(350)
        self.content_layout.addWidget(self.ph_input)

        self.crop_type_input = LineEdit(self)
        self.crop_type_input.setPlaceholderText('请输入作物种类')
        self.crop_type_input.setMaximumWidth(350)
        self.content_layout.addWidget(self.crop_type_input)

        # 模型选择下拉框
        self.model_selector = ComboBox(self)
        self.model_selector.addItems(["随机森林回归", "CART决策树回归", 
                                   "XGBoost回归","优化后的CART决策树回归", "优化后的XGBoost回归"])
        self.model_selector.setMaximumWidth(350)
        self.content_layout.addWidget(self.model_selector)

        # 创建水平布局用于放置按钮
        self.buttons_layout = QHBoxLayout()

        # 预测产量按钮
        self.predict_button = PushButton('预测产量', self)
        self.predict_button.setToolTip('✨点击进行产量的预测,结果显示在结果框中✨')
        # self.predict_button.setToolTipDuration(2000)
        # 给按钮安装工具提示过滤器
        self.predict_button.installEventFilter(ToolTipFilter(self.predict_button, showDelay=1000, position=ToolTipPosition.TOP))
        self.predict_button.setMaximumWidth(150)
        self.predict_button.clicked.connect(self.on_predict_button_click)
        self.buttons_layout.addWidget(self.predict_button)

        # 训练所有模型按钮
        self.train_button = PushButton('预训练模型', self)
        self.train_button.setToolTip('✨点击预训练模型,包括一个种类的模型下的全部作物种类✨')
        # self.train_button.setToolTipDuration(2000)
        # 给按钮安装工具提示过滤器
        self.train_button.installEventFilter(ToolTipFilter(self.train_button, showDelay=1000, position=ToolTipPosition.TOP))
        self.train_button.setMaximumWidth(150)
        self.train_button.clicked.connect(self.on_train_all_models_button_click)
        self.buttons_layout.addWidget(self.train_button)

        # 将按钮布局添加到内容布局
        self.content_layout.addLayout(self.buttons_layout)

        # 显示结果的标签
        self.result_label = PushButton('预测结果将在此显示', self)
        self.result_label.setFont(QFont('Arial', 15, QFont.Bold))
        self.result_label.setMinimumHeight(170)
        self.result_label.setMaximumWidth(350)
        self.result_label.clicked.connect(self.on_result_label_button_click)
        self.result_label.setToolTip('✨点击触发彩蛋✨')
        self.result_label.installEventFilter(ToolTipFilter(self.result_label, showDelay=1000, position=ToolTipPosition.TOP))
        self.content_layout.addWidget(self.result_label)

        # 添加内容布局到主布局
        self.main_layout.addLayout(self.content_layout)

        # 添加底部伸展，使控件整体居中
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 设置主布局
        self.setLayout(self.main_layout)


    def centerWindow(self):
        # 窗口居中
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_center = screen_geometry.center()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

    def load_data(self):
        # 加载并处理数据
        file_path = os.path.join(os.path.dirname(get_current_directory()), 'product_regressiondb.csv')

        self.data = pd.read_csv(file_path)
        self.data.rename(columns={'Rainfall': '降雨量', 'Temperature': '气温', 'Ph': 'ph值', 'Crop': '作物种类', 'Production': '产量'}, inplace=True)
        self.data.drop_duplicates(inplace=True)
        self.data.reset_index(drop=True, inplace=True)

        self.data_cleaned = pd.DataFrame()
        groups = self.data.groupby('作物种类')
        for crop, group in groups:
            z_scores = group[['降雨量', '气温', 'ph值', '产量']].apply(zscore)
            outliers = (z_scores > 3) | (z_scores < -3)
            group_cleaned = group[~outliers.any(axis=1)]
            self.data_cleaned = pd.concat([self.data_cleaned, group_cleaned])
        self.data_processed = self.data_cleaned

    def get_selected_model_type(self):
        """获取用户选择的模型类型"""
        selected_text = self.model_selector.currentText()
        
        if "随机森林" in selected_text:
            return "RandomForest"
        elif "优化后的CART决策树" in selected_text:
            return "DecisionTreeOptimized"
        elif "CART决策树" in selected_text:
            return "DecisionTree"
        elif "优化后的XGBoost" in selected_text:
            return "XGBoostOptimized"
        elif "XGBoost" in selected_text:
            return "XGBoost"
       
        else:
            raise ValueError(f"未知的模型类型: {selected_text}")

    def on_predict_button_click(self):
        try:
            rainfall = float(self.rainfall_input.text())
            temperature = float(self.temperature_input.text())
            ph_value = float(self.ph_input.text())
            crop_type = self.crop_type_input.text().strip()
            model_type = self.get_selected_model_type()
            predicted_yield = self.predict_yield(rainfall, temperature, ph_value, crop_type, model_type)
            print(predicted_yield)
            self.result_label.setText(f"预测的产量: {predicted_yield:.6f} 吨/公顷")
        except KeyError:
            # 捕获作物种类无效时的异常
            InfoBar.warning(
                title='输入错误',
                content="请输入有效的作物种类！",
                orient=Qt.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
        except ValueError:
            # 捕获数值转换失败等输入错误
            InfoBar.error(
                title='输入错误',
                content="请确保所有输入字段正确！",
                orient=Qt.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
        )
        
        
    def get_next_content(self):
        # 循环取出下一个内容
        content = self.contents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.contents)
        return content    

    def predict_yield(self, rainfall, temperature, ph_value, crop_type, model_type):
        model_dir = os.path.join(os.path.dirname(get_current_directory()), "models")
        
        if crop_type not in self.data_processed['作物种类'].unique():
            raise KeyError("无效的作物种类")

        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        model_filename = os.path.join(model_dir, f"{model_type}_model_crop_{crop_type}.pkl")

        if os.path.exists(model_filename):
            model = joblib.load(model_filename)
        else:
            return self.retrain_and_predict(rainfall, temperature, ph_value, crop_type, model_type)

        input_data = pd.DataFrame([[rainfall, temperature, ph_value]], columns=['降雨量', '气温', 'ph值'])
        predicted_yield = model.predict(input_data)
        return predicted_yield[0]

    def retrain_and_predict(self, rainfall, temperature, ph_value, crop_type, model_type):
        crop_data = self.data_processed[self.data_processed['作物种类'] == crop_type]
        X_crop = crop_data[['降雨量', '气温', 'ph值']]
        y_crop = crop_data['产量']

        # 根据模型类型获取相应的模型
        if model_type == "RandomForest":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == "DecisionTree":
            model = DecisionTreeRegressor(random_state=42)
        elif model_type == "XGBoost":
            model = XGBRegressor(objective="reg:squarederror", random_state=42)
        elif model_type == "DecisionTreeOptimized":
             # 使用之前优化得到的最佳超参数
            best_params_cart = [20, 3, 1]  # 从粒子群优化得到的最佳超参数
            model= DecisionTreeRegressor(max_depth=best_params_cart[0], 
                                              min_samples_split=best_params_cart[1], 
                                              min_samples_leaf=best_params_cart[2], 
                                              random_state=42)
        elif model_type == "XGBoostOptimized":
            best_params_xgb = [200, 10, 2, 0.09713775005616568] 
            model = XGBRegressor(n_estimators=int(best_params_xgb[0]),
                                 max_depth=int(best_params_xgb[1]),
                                 learning_rate=best_params_xgb[3],
                                 random_state=42)
        else:
            raise ValueError(f"未知的模型类型: {model_type}")

        # 训练模型
        model.fit(X_crop, y_crop)

        # 保存模型
        model_dir = os.path.join(os.path.dirname(get_current_directory()), "models")
        model_filename = os.path.join(model_dir, f"{model_type}_model_crop_{crop_type}.pkl")
        joblib.dump(model, model_filename)

        # 返回预测结果
        input_data = pd.DataFrame([[rainfall, temperature, ph_value]], columns=['降雨量', '气温', 'ph值'])
        predicted_yield = model.predict(input_data)
        return predicted_yield[0]
    
    def on_result_label_button_click(self):
        content = self.get_next_content()
        InfoBar.info(
                title='',
                content=content,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self)


    def on_train_all_models_button_click(self):
        # 禁用按钮
        self.train_button.setEnabled(False)
    
        # 提示训练开始
        InfoBar.info(
            title='训练开始',
            content="开始训练模型！",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,  # 提示显示时间（毫秒）
            parent=self
        )

        # 获取用户选择的模型类型
        model_type = self.get_selected_model_type()
    
        # 启动模型训练
        self.train_thread = TrainModelsThread(self.data_processed, model_type)
    
        # 连接信号：训练完成后调用 on_training_finished
        self.train_thread.finished_signal.connect(self.on_training_finished)
    
        # 启动线程
        self.train_thread.start()

    def on_training_finished(self):
        # 提示训练完成
        InfoBar.success(
            title='训练完成',
            content="模型训练完成！",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,  # 提示显示时间（毫秒）
            parent=self
        )
        # 启用按钮
        self.train_button.setEnabled(True)



from qfluentwidgets import PushButton


class PredictPage(Ui_predictpage,QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)



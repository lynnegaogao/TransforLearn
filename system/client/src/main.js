import { createApp } from 'vue'
import App from './App.vue'
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/antd.css';
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// import { Button, Row, Col } from 'ant-design-vue';
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App);
app.config.productionTip = false;

app.use(Antd);
// app.use(Button).use(Row).use(Col);

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app
  .use(ElementPlus)
  .mount('#app')

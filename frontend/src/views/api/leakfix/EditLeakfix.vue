<template>
  <div class="system-edit-menu-container">
    <el-dialog
        draggable
        :title="state.editType === 'save'? '新增' : '修改'" v-model="state.isShowDialog"
        width="30%">
      <el-form ref="formRef" :model="state.form" :rules="state.rules" label-width="80px">
        <el-row :gutter="35">


          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="文件名称" prop="name">
              <el-input v-model="state.form.name" placeholder="文件名称" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="文件地址" prop="url">
              <el-input v-model="state.form.url" placeholder="文件地址" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="下载地址" prop="addr">
              <el-input v-model="state.form.addr" placeholder="下载地址" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="文件MD5" prop="md5">
              <el-input v-model="state.form.md5" placeholder="文件MD5" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="文件大小" prop="size">
              <el-input v-model="state.form.size" placeholder="文件大小" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="更新时间" prop="c_time">
              <el-input v-model="state.form.c_time" placeholder="更新时间" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="备注">
              <el-input v-model="state.form.remark" placeholder="备注" clearable></el-input>
            </el-form-item>
          </el-col>

        </el-row>
      </el-form>
      <template #footer>
				<span class="dialog-footer">
					<el-button @click="onCancel">取 消</el-button>
					<el-button type="primary" @click="saveOrUpdate">保 存</el-button>
				</span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="saveOrUpdateLeakfix">
import {reactive, ref} from 'vue';
import {ElMessage} from "element-plus";
import {userLeakfixApi} from "/src/api/useServersApi/leaks";

const emit = defineEmits(["getList"])

const createForm = () => {
  return {
    name: '', // 项目名称
    url: '',
    addr: '',
    size: 0,
    md5: '',
    c_time: '',
    remark: ''
  }
}
const formRef = ref()
const state = reactive({
  isShowDialog: false,
  editType: '',
  // 参数请参考 `/src/router/route.ts` 中的 `dynamicRoutes` 路由菜单格式
  form: createForm(),
  rules: {
    url: [{required: true, message: '请输入文件地址', trigger: 'blur'},],
    name: [{required: true, message: '请输入名称', trigger: 'blur'},],
    addr: [{required: true, message: '请输入下载地址', trigger: 'blur'},],
    size: [{required: true, message: '请输入文件大小', trigger: 'blur'},],
    md5: [{required: true, message: '请输入文件MD5', trigger: 'blur'},],
    c_time: [{required: true, message: '请输入文件更新时间', trigger: 'blur'},],
  },
  menuData: [], // 上级菜单数据
  systemList: [{"id": 0, "name": "未知"}, {"id": 1, "name": "linux"}, {"id": 2, "name": "ubuntu"}, {
    "id": 3,
    "name": "mac"
  }, {"id": 4, "name": "windows"}],
});


// 打开弹窗
const openDialog = (type, row) => {
  state.editType = type
  if (row) {
    state.form = JSON.parse(JSON.stringify(row));
  } else {
    state.form = createForm()
  }
  state.isShowDialog = true;
};
// 关闭弹窗
const closeDialog = () => {
  state.isShowDialog = false;
};
// 取消
const onCancel = () => {
  closeDialog();
};
// 新增
const saveOrUpdate = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      userLeakfixApi().saveOrUpdate(state.form)
          .then((res) => {
              ElMessage.success('操作成功');
              emit('getList')
              closeDialog(); // 关闭弹窗

          })
      console.log(state.form, 'state.menuForm')
    }
  })

};

defineExpose({
  openDialog,
})

</script>

<template>
  <div class="system-edit-menu-container">
    <el-dialog
        draggable
        :title="state.editType === 'save'? '新增' : '修改'" v-model="state.isShowDialog"
        width="30%">
      <el-form ref="formRef" :model="state.form" :rules="state.rules" label-width="80px">
        <el-row :gutter="35">


          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="服务器IP" prop="ip">
              <el-input v-model="state.form.ip" placeholder="服务器IP" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="项目名称" prop="name">
              <el-input v-model="state.form.name" placeholder="项目名称" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="管控版本" prop="name">
              <el-input v-model="state.form.epp_version" placeholder="管控版本" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="CPU">
              <el-input v-model="state.form.cpu" placeholder="cpu" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="内存/GB">
              <el-input v-model="state.form.mem" placeholder="内存" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="磁盘/GB">
              <el-input v-model="state.form.disk_total" placeholder="磁盘" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="服务器性质">
              <el-input v-model="state.form.server_type" placeholder="服务器性质" clearable></el-input>
            </el-form-item>
          </el-col>


          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="操作系统" prop="system_type">
              <el-select v-model="state.form.system_type" clearable placeholder="操作系统" style="width: 100%">
                <el-option
                    v-for="item in state.systemList"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                >
                </el-option>
              </el-select>
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

<script setup name="saveOrUpdateServerIp">
import {reactive, ref} from 'vue';
import {ElMessage} from "element-plus";
import {userServerIpApi} from "/src/api/useServersApi/serverIp";

const emit = defineEmits(["getList"])

const createForm = () => {
  return {
    ip: '',
    name: '', // 项目名称
    epp_version: '',
    cpu: 0,
    mem: 0.0,
    disk_total: 0.0,
    system_type: '',
    server_type: '',
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
    ip: [{required: true, message: '请输入服务器IP', trigger: 'blur'},],
    name: [{required: true, message: '请输入名称', trigger: 'blur'},],
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
    // console.log('validate is value:', valid)
    if (valid) {
      userServerIpApi().saveOrUpdate(state.form)
          .then((res) => {
            console.log("res is value:", res)
            if (res.detail  &&  res.detail.code === 11001) {
              ElMessage.error('只读用户权限限制');
            } else {
              ElMessage.success('操作成功');
              emit('getList')
              closeDialog(); // 关闭弹窗
            }

          })
      console.log(state.form, 'state.menuForm')
    }
  })

};

defineExpose({
  openDialog,
})

</script>

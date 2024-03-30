<template>
  <div class="app-container">
    <el-card>
      <div class="mb15">
        <el-input v-model="state.listQuery.name" placeholder="请输入服务器名称" style="max-width: 180px"></el-input>
        <el-input v-model="state.listQuery.ip" placeholder="请输入服务器IP" style="max-width: 180px"></el-input>
        <el-input v-model="state.listQuery.epp_version" placeholder="请输入管控版本" style="max-width: 180px"></el-input>
        <el-button type="primary" class="ml10" @click="search">查询
        </el-button>
        <el-button type="success" class="ml10" @click="onOpenSaveOrUpdate('save', null)">新增
        </el-button>
      </div>
      <z-table
          :columns="state.columns"
          ref="tableRef"
          :data="state.listData"
          v-model:page-size="state.listQuery.pageSize"
          v-model:page="state.listQuery.page"
          :total="state.total"
          @pagination-change="getList"
      >
      </z-table>
    </el-card>
    <Edit ref="EditRef" @getList="getList"/>
  </div>
</template>

<script setup name="apiServerip">
import {defineAsyncComponent, h, onMounted, reactive, ref} from 'vue';
import {ElButton, ElMessage, ElMessageBox, ElTag} from 'element-plus';
import {userServerIpApi} from "/src/api/useServersApi/serverIp";
import {getStatusTag} from "/@/utils/case";

// 引入组件
const Edit = defineAsyncComponent(() => import("./EditServerIp.vue"))

// 自定义数据
const tableRef = ref();
const EditRef = ref();
const state = reactive({
  columns: [
    {label: '序号', columnType: 'index', align: 'center', width: 'auto', show: true},
    {
      key: 'name', label: '服务器名称', align: 'center', width: '140', show: true,
      render: ({row}) => h(ElButton, {
        link: true,
        type: "primary",
        onClick: () => {
          onOpenSaveOrUpdate("update", row)
        }
      }, () => row.name)
    },
    {key: 'ip', label: '服务器IP', align: 'center', width: '100', show: true},
    {key: 'epp_version', label: '管控版本', align: 'center', width: '100', show: true},

    {key: 'is_install', label: '安装状态', align: 'center', width: '', show: true,
      render: ({row}) => h(ElTag, {
          type: row.is_install == 2 ? "success" : "danger",
        }, () => row.is_install == 1 ? "未安装" : row.is_install == 2 ? "已安装" : "未知",)

    },
    {key: 'is_run', label: '运行状态', align: 'center', width: '', show: true,
      render: ({row}) => h(ElTag, {
          type: row.is_run == 2 ? "success" : "",
        }, () => row.is_run == 1 ? "未运行" : row.is_install == 2 ? "已运行" : "未知",)
    },
    {key: 'is_multi', label: '多级状态', align: 'center', width: '', show: true,
      render: ({row}) => h(ElTag, {
        }, () => state.multiType[row.is_multi] || '未知')
    },
    {key: 'server_type', label: '服务器性质', align: 'center', width: '', show: true,
      render: ({row}) => row.server_type ? h(ElTag,{
        type: getStatusTag(row.status),
      }, () => row.server_type) : "-"
    },

    {key: 'system_type', label: '操作系统', align: 'center', width: '', show: true,
       render: ({row}) => h(ElTag, {
        }, () => state.systemType[row.system_type])
    },
    {key: 'server_source', label: '服务器来源', align: 'center', width: '', show: true,
      // 接口返回空或者null，转换为-   参考reportdetail.vue
      render: ({row}) => row.server_source ? h(ElTag, {
        type: getStatusTag(row.status),
        // type: "",
      }, () => row.server_source) : "-"
    },

    {key: 'cpu', label: 'cpu', align: 'center', width: '', show: true},
    {key: 'mem', label: '内存/GB', align: 'center', width: '', show: true},
    {key: 'disk_total', label: '磁盘总量/GB', align: 'center', width: '', show: true},
    {key: 'disk_use', label: '磁盘使用/GB', align: 'center', width: '', show: true},
    {key: 'remark', label: '备注', align: 'center', width: '', show: true},
    {key: 'updation_date', label: '更新时间', align: 'center', width: '150', show: true},
    {key: 'creation_date', label: '创建时间', align: 'center', width: '150', show: true},
    {key: 'updated_by_name', label: '更新人', align: 'center', width: '', show: true},
    {key: 'created_by_name', label: '创建人', align: 'center', width: '', show: true},
    {
      label: '操作', fixed: 'right', width: '140', align: 'center',
      render: ({row}) => h("div", null, [
        h(ElButton, {
          type: "primary",
          onClick: () => {
            onOpenSaveOrUpdate("update", row)
          }
        }, () => '编辑'),

        h(ElButton, {
          type: "danger",
          onClick: () => {
            deleted(row)
          }
        }, () => '删除')
      ])
    },
  ],
  listData: [],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    name: '',
  },
  systemType: {
    0: "未知",
    1: "linux",
    2: "ubuntu",
    3: "mac",
    4: "windows"
  },
  multiType: {
    0: "未知",
    1: "仅本级",
    2: "包含下级",
    4: "为下级"
  }
});

// 初始化表格数据
const getList = () => {
  tableRef.value.openLoading()
    userServerIpApi().getList(state.listQuery)
      .then(res => {
        state.listData = res.data.rows
        state.total = res.data.rowTotal
        tableRef.value.closeLoading()
      })
      .finally(() => {
        tableRef.value.closeLoading()
      })
};
// 查询
const search = () => {
  state.listQuery.page = 1
  getList()
}

// 新增或修改角色
const onOpenSaveOrUpdate = (editType, row) => {
  EditRef.value.openDialog(editType, row);
};

// 删除角色
const deleted = (row) => {
  ElMessageBox.confirm('是否删除该条数据, 是否继续?', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
      .then(() => {
        userServerIpApi().deleted({id: row.id})
            .then(() => {
              ElMessage.success('删除成功');
              getList()
            })
      })
      .catch(() => {
      });
};
// 页面加载时
onMounted(() => {
  getList();
});

</script>

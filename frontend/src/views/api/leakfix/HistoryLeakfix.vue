<template>
  <div class="app-container">
    <el-card>
      <div class="mb15">
        <el-input v-model="state.listQuery.name" placeholder="请输入文件名称" style="max-width: 180px"></el-input>
        <el-button type="primary" class="ml10" @click="search">查询
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

<script setup name="HistoryLeakfix">
import {defineAsyncComponent, h, onMounted, reactive, ref} from 'vue';
import {ElButton, ElDropdown, ElDropdownItem, ElDropdownMenu, ElMessage, ElMessageBox} from 'element-plus';
import {userLeakfixApi} from "/src/api/useServersApi/leaks";
import {MoreFilled} from "@element-plus/icons";
import {useRoute} from "vue-router";

// 引入组件
const Edit = defineAsyncComponent(() => import("./EditLeakfix.vue"))

// 自定义数据
const tableRef = ref();
const EditRef = ref();
const route = useRoute();

const state = reactive({
  columns: [
    {label: '序号', columnType: 'index', align: 'center', width: 'auto', show: true},
    {
      key: 'name', label: '文件名称', align: 'center', width: '140', show: true,
      render: ({row}) => h(ElButton, {
        link: true,
        type: "primary",
        onClick: () => {
          onOpenSaveOrUpdate("update", row)
        }
      }, () => row.name)
    },
    {key: 'intro', label: '简介', align: 'center', width: '100', show: true
    },
    {key: 'url', label: '文件地址', align: 'center', width: '100', show: true},

    {key: 'md5', label: '文件MD5', align: 'center', width: '', show: true},
    {key: 'c_time', label: '更新时间', align: 'center', width: '', show: true},
    // {key: 'addr', label: 'addr', align: 'center', width: '', show: false},

    {
      label: '操作', fixed: 'right', width: '200', align: 'center',
      render: ({row}) => h("div", null, [

        h(ElButton, {
          type: "primary",
          onClick: () => {
            download("download", row)

          }
        }, () => '下载'),

        h(ElButton, {
          type: "primary",
          onClick: () => {
            onOpenSaveOrUpdate("update", row)
          }
        }, () => '编辑'),

        h(ElDropdown, {
              style: {
                verticalAlign: "middle",
                marginLeft: "12px"
              }
            },
            {
              default: () => h(ElButton, {
                style: {},
                link: true,
                icon: MoreFilled
              }),
              dropdown: () => h(ElDropdownMenu, {
                    style: {
                      minWidth: "100px"
                    },
                  },
                  {
                    default: () => [
                      h(ElDropdownItem, {
                        style: {
                          color: "var(--el-color-primary)"
                        },
                        onClick: () => {
                          onOpenSaveOrUpdate("detail", row)
                        }
                      }, () => '详情'),

                      h(ElDropdownItem, {
                        style: {
                          color: "var(--el-color-danger)"
                        },
                        onClick: () => {
                          deleted(row)
                        }
                      }, () => '删除'),
                    ]
                  }
              )
            }
        ),
      ])
    },
  ],
  listData: [],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    name: route.query.name,
  },
  leakInfo: {}

});

// 初始化表格数据
const getList = () => {
  tableRef.value.openLoading()
    userLeakfixApi().getHistoryList(state.listQuery)
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
        userLeakfixApi().deleted({id: row.id})
            .then(() => {
              ElMessage.success('删除成功');
              getList()
            })
      })
      .catch(() => {
      });
};





const download = (type, row) => {

  // 文件放在前端/public目录下则可以下载
  // https://juejin.cn/post/7117924968171569166
  let a = document.createElement('a'); //创建一个<a></a>标签
    a.href = 'static/downloads/' + row.addr; // 给a标签的href属性值加上地址，注意，这里是绝对路径，不用加 点.
    a.download = row.name; //设置下载文件文件名，这里加上.xlsx指定文件类型，pdf文件就指定.fpd即可
    a.style.display = 'none'; // 障眼法藏起来a标签
    document.body.appendChild(a); // 将a标签追加到文档对象中
    a.click(); // 模拟点击了a标签，会触发a标签的href的读取，浏览器就会自动下载了
    a.remove(); // 一次性的，用完就删除a标签

//   axios({
//   url: row.addr,
//   method: 'get',
//   responseType: 'blob' // 设置响应数据类型为二进制数据流
// }).then(res => {
//   const blob = new Blob([res.data])
//   const link = document.createElement('a')
//   link.href = window.URL.createObjectURL(blob)
//   link.download = row.name
//   link.click()
// })



  // const a = document.createElement('a')
  // console.log('row_value:', row)
  //  a.download = row.name
  //  // 文本txt类型
  //  const blob = new Blob([row.addr], {type: 'text/plain'})
  //  // text指需要下载的文本或字符串内容
  //  a.href = window.URL.createObjectURL(blob)
  //  // 会生成一个类似blob:http://localhost:8080/d3958f5c-0777-0845-9dcf-2cb28783acaf 这样的URL字符串
  //  document.body.appendChild(a)
  //  a.click()
  //  a.remove()





  // userLeakfixApi().download(row).then((res => {
  //   ElMessage.success('下载成功');
  // }))

};





// 页面加载时
onMounted(() => {
  getList();
});




</script>

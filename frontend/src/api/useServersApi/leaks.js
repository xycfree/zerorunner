import request from '/src/utils/request';
import axios from "axios";

/**
 * 项目使用接口
 * @method getProjectList 获取项目列表
 * @method getMenuTest 获取后端动态路由菜单(test)
 */
export function userLeakfixApi() {
    return {
        getList: (data) => {
            return request({
                url: '/leaks/list',
                method: 'POST',
                data,
            });
        },
        saveOrUpdate(data) {
            return request({
                url: '/leaks/saveOrUpdate',
                method: 'POST',
                data
            })
        },
        deleted: (data) => {
            return request({
                url: '/leaks/deleted',
                method: 'POST',
                data,
            });
        },

        // download: (data) => {
        //     /* 文件下载，需要get请求，采用二进制流形式下载blob */
        //     return request({
        //         url: '/leaks/download/' + String(data.id),
        //         method: 'GET',
        //         responseType: 'blob'
        //
        //     }).then(res => {
        //       const blob = new Blob([res.data])
        //       const link = document.createElement('a')
        //       link.href = window.URL.createObjectURL(blob)
        //       link.download = data.name
        //       link.click()
        //         }).catch(function (err) {
        //             console.log("下载异常:", err)
        //     })
        // },

        //start

        download: (d) => {
        return request({
                method: 'get',
                url: '/leaks/download/' + String(d.id),
                responseType: 'blob'
            }).then(res => {
                const { data } = res
                const blob = new Blob([data])
                // let disposition = decodeURI(res.headers['content-disposition'])
                // 从响应头中获取文件名称
                // let fileName = disposition.substring(disposition.indexOf('fileName=') + 9, disposition.length)
                if ('download' in document.createElement('a')) {
                    // 非IE下载
                    const elink = document.createElement('a')
                    elink.download = d.name
                    elink.style.display = 'none'
                    elink.href = URL.createObjectURL(blob)
                    document.body.appendChild(elink)
                    elink.click()
                    URL.revokeObjectURL(elink.href) // 释放URL 对象
                    document.body.removeChild(elink)
                } else {
                    // IE10+下载
                    navigator.msSaveBlob(blob, d.name)
                }
            }).catch((error) => {
                    console.log(error)
            })

                },


        //end


        getHistoryList: (data) => {
            return request({
                url: '/leaks/history/list',
                method: 'POST',
                data,
            });
        },


    }
}

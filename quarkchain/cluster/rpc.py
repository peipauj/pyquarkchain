from quarkchain.core import hash256, uint16, uint32, uint64, uint128, uint256, boolean
from quarkchain.core import (
    Transaction,
    PreprendedSizeBytesSerializer, PreprendedSizeListSerializer, Serializable, Address, Branch, ShardMask
)
from quarkchain.cluster.core import (
    MinorBlock,
    MinorBlockHeader,
    RootBlock,
    CrossShardTransactionList,
    TransactionReceipt,
)

# RPCs to initialize a cluster


class Ping(Serializable):
    FIELDS = [
        ("id", PreprendedSizeBytesSerializer(4)),
        ("shardMaskList", PreprendedSizeListSerializer(4, ShardMask)),
        ("rootTip", RootBlock),
    ]

    def __init__(self, id, shardMaskList, rootTip):
        """ Empty shardMaskList means root """
        if isinstance(id, bytes):
            self.id = id
        else:
            self.id = bytes(id, "ascii")
        self.shardMaskList = shardMaskList
        self.rootTip = rootTip


class Pong(Serializable):
    FIELDS = [
        ("id", PreprendedSizeBytesSerializer(4)),
        ("shardMaskList", PreprendedSizeListSerializer(4, ShardMask)),
    ]

    def __init__(self, id, shardMaskList):
        """ Empty slaveId and shardMaskList means root """
        if isinstance(id, bytes):
            self.id = id
        else:
            self.id = bytes(id, "ascii")
        self.shardMaskList = shardMaskList


class SlaveInfo(Serializable):
    FIELDS = [
        ("id", PreprendedSizeBytesSerializer(4)),
        ("ip", uint128),
        ("port", uint16),
        ("shardMaskList", PreprendedSizeListSerializer(4, ShardMask)),
    ]

    def __init__(self, id, ip, port, shardMaskList):
        if isinstance(id, bytes):
            self.id = id
        else:
            self.id = bytes(id, "ascii")
        self.ip = ip
        self.port = port
        self.shardMaskList = shardMaskList


class ConnectToSlavesRequest(Serializable):
    ''' Master instructs a slave to connect to other slaves '''
    FIELDS = [
        ("slaveInfoList", PreprendedSizeListSerializer(4, SlaveInfo)),
    ]

    def __init__(self, slaveInfoList):
        self.slaveInfoList = slaveInfoList


class ConnectToSlavesResponse(Serializable):
    ''' resultList must have the same size as salveInfoList in the request.
    Empty result means success otherwise it would a serialized error message.
    '''
    FIELDS = [
        ("resultList", PreprendedSizeListSerializer(4, PreprendedSizeBytesSerializer(4))),
    ]

    def __init__(self, resultList):
        self.resultList = resultList


class GetMinorBlockRequest(Serializable):
    FIELDS = [
        ("branch", Branch),
        ("minorBlockHash", hash256),
        ("height", uint64),
    ]

    def __init__(self, branch, minorBlockHash=None, height=0):
        self.branch = branch
        self.minorBlockHash = minorBlockHash if minorBlockHash else bytes(32)
        self.height = height


class GetMinorBlockResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
        ("minorBlock", MinorBlock),
    ]

    def __init__(self, errorCode, minorBlock):
        self.errorCode = errorCode
        self.minorBlock = minorBlock


class GetTransactionRequest(Serializable):
    FIELDS = [
        ("txHash", hash256),
        ("branch", Branch),
    ]

    def __init__(self, txHash, branch):
        self.txHash = txHash
        self.branch = branch


class GetTransactionResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
        ("minorBlock", MinorBlock),
        ("index", uint32)
    ]

    def __init__(self, errorCode, minorBlock, index):
        self.errorCode = errorCode
        self.minorBlock = minorBlock
        self.index = index


class ExecuteTransactionRequest(Serializable):
    FIELDS = [
        ("tx", Transaction),
    ]

    def __init__(self, tx):
        self.tx = tx


class ExecuteTransactionResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
        ("result", PreprendedSizeBytesSerializer(4))
    ]

    def __init__(self, errorCode, result):
        self.errorCode = errorCode
        self.result = result


class GetTransactionReceiptRequest(Serializable):
    FIELDS = [
        ("txHash", hash256),
        ("branch", Branch),
    ]

    def __init__(self, txHash, branch):
        self.txHash = txHash
        self.branch = branch


class GetTransactionReceiptResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
        ("minorBlock", MinorBlock),
        ("index", uint32),
        ("receipt", TransactionReceipt),
    ]

    def __init__(self, errorCode, minorBlock, index, receipt):
        self.errorCode = errorCode
        self.minorBlock = minorBlock
        self.index = index
        self.receipt = receipt


# RPCs to update blockchains

# master -> slave

class AddRootBlockRequest(Serializable):
    ''' Add root block to each slave
    '''
    FIELDS = [
        ("rootBlock", RootBlock),
        ("expectSwitch", boolean),
    ]

    def __init__(self, rootBlock, expectSwitch):
        self.rootBlock = rootBlock
        self.expectSwitch = expectSwitch


class AddRootBlockResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
        ("switched", boolean),
    ]

    def __init__(self, errorCode, switched):
        self.errorCode = errorCode
        self.switched = switched


class EcoInfo(Serializable):
    ''' Necessary information for master to decide the best block to mine '''
    FIELDS = [
        ("branch", Branch),
        ("height", uint64),
        ("coinbaseAmount", uint256),
        ("difficulty", uint64),
        ("unconfirmedHeadersCoinbaseAmount", uint256)
    ]

    def __init__(self, branch, height, coinbaseAmount, difficulty, unconfirmedHeadersCoinbaseAmount):
        self.branch = branch
        self.height = height
        self.coinbaseAmount = coinbaseAmount
        self.difficulty = difficulty
        self.unconfirmedHeadersCoinbaseAmount = unconfirmedHeadersCoinbaseAmount


class GetEcoInfoListRequest(Serializable):
    FIELDS = []

    def __init__(self):
        pass


class GetEcoInfoListResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
        ("ecoInfoList", PreprendedSizeListSerializer(4, EcoInfo)),
    ]

    def __init__(self, errorCode, ecoInfoList):
        self.errorCode = errorCode
        self.ecoInfoList = ecoInfoList


class ArtificialTxConfig(Serializable):
    FIELDS = [
        ("numTxPerBlock", uint32),
        ("xShardTxPercent", uint32),  # [0,100]
    ]

    def __init__(self, numTxPerBlock, xShardTxPercent):
        self.numTxPerBlock = numTxPerBlock
        self.xShardTxPercent = xShardTxPercent


class GetNextBlockToMineRequest(Serializable):
    FIELDS = [
        ("branch", Branch),
        ("address", Address),
        ("artificialTxConfig", ArtificialTxConfig),
    ]

    def __init__(self, branch, address, artificialTxConfig):
        self.branch = branch
        self.address = address
        self.artificialTxConfig = artificialTxConfig


class GetNextBlockToMineResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
        ("block", MinorBlock),
    ]

    def __init__(self, errorCode, block):
        self.errorCode = errorCode
        self.block = block


class AddMinorBlockRequest(Serializable):
    FIELDS = [
        ("minorBlockData", PreprendedSizeBytesSerializer(4)),
    ]

    def __init__(self, minorBlockData):
        self.minorBlockData = minorBlockData


class AddMinorBlockResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
    ]

    def __init__(self, errorCode):
        self.errorCode = errorCode


class HeadersInfo(Serializable):
    FIELDS = [
        ("branch", Branch),
        ("headerList", PreprendedSizeListSerializer(4, MinorBlockHeader)),
    ]

    def __init__(self, branch, headerList):
        self.branch = branch
        self.headerList = headerList


class GetUnconfirmedHeadersRequest(Serializable):
    FIELDS = []

    def __init__(self):
        pass


class GetUnconfirmedHeadersResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
        ("headersInfoList", PreprendedSizeListSerializer(4, HeadersInfo)),
    ]

    def __init__(self, errorCode, headersInfoList):
        self.errorCode = errorCode
        self.headersInfoList = headersInfoList


class GetAccountDataRequest(Serializable):
    FIELDS = [
        ("address", Address),
    ]

    def __init__(self, address):
        self.address = address


class AccountBranchData(Serializable):
    FIELDS = [
        ("branch", Branch),
        ("transactionCount", uint256),
        ("balance", uint256),
    ]

    def __init__(self, branch, transactionCount, balance):
        self.branch = branch
        self.transactionCount = transactionCount
        self.balance = balance


class GetAccountDataResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
        ("accountBranchDataList", PreprendedSizeListSerializer(4, AccountBranchData)),
    ]

    def __init__(self, errorCode, accountBranchDataList):
        self.errorCode = errorCode
        self.accountBranchDataList = accountBranchDataList


class AddTransactionRequest(Serializable):
    FIELDS = [
        ("tx", Transaction),
    ]

    def __init__(self, tx):
        self.tx = tx


class AddTransactionResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
    ]

    def __init__(self, errorCode):
        self.errorCode = errorCode


class SyncMinorBlockListRequest(Serializable):
    FIELDS = [
        ("minorBlockHashList", PreprendedSizeListSerializer(4, hash256)),
        ("branch", Branch),
        ("clusterPeerId", uint64),
    ]

    def __init__(self, minorBlockHashList, branch, clusterPeerId):
        self.minorBlockHashList = minorBlockHashList
        self.branch = branch
        self.clusterPeerId = clusterPeerId


class SyncMinorBlockListResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
    ]

    def __init__(self, errorCode):
        self.errorCode = errorCode


# Virtual connection management
class CreateClusterPeerConnectionRequest(Serializable):
    ''' Broadcast to the cluster and announce that a peer connection is created
    Assume always succeed.
    '''
    FIELDS = [
        ("clusterPeerId", uint64)
    ]

    def __init__(self, clusterPeerId):
        self.clusterPeerId = clusterPeerId


class CreateClusterPeerConnectionResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32)
    ]

    def __init__(self, errorCode):
        self.errorCode = errorCode


class DestroyClusterPeerConnectionCommand(Serializable):
    ''' Broadcast to the cluster and announce that a peer connection is lost
    As a contract, the master will not send traffic after the command.
    '''
    FIELDS = [
        ("clusterPeerId", uint64)
    ]

    def __init__(self, clusterPeerId):
        self.clusterPeerId = clusterPeerId


# slave -> master


class ShardStats(Serializable):
    FIELDS = [
        ("branch", Branch),
        ("height", uint64),
        ("timestamp", uint64),
        ("txCount60s", uint32),
        ("pendingTxCount", uint32),
        ("blockCount60s", uint32),
        ("staleBlockCount60s", uint32),
        ("lastBlockTime", uint32),
    ]

    def __init__(
        self,
        branch,
        height,
        timestamp,
        txCount60s,
        pendingTxCount,
        blockCount60s,
        staleBlockCount60s,
        lastBlockTime,
    ):
        self.branch = branch
        self.height = height
        self.timestamp = timestamp
        self.txCount60s = txCount60s
        self.pendingTxCount = pendingTxCount
        self.blockCount60s = blockCount60s
        self.staleBlockCount60s = staleBlockCount60s
        self.lastBlockTime = lastBlockTime


class AddMinorBlockHeaderRequest(Serializable):
    ''' Notify master about a successfully added minro block.
    Piggyback the ShardStats in the same request.
    '''
    FIELDS = [
        ("minorBlockHeader", MinorBlockHeader),
        ("txCount", uint32),  # the total number of tx in the block
        ("xShardTxCount", uint32),  # the number of xshard tx in the block
        ("shardStats", ShardStats),
    ]

    def __init__(self, minorBlockHeader, txCount, xShardTxCount, shardStats):
        self.minorBlockHeader = minorBlockHeader
        self.txCount = txCount
        self.xShardTxCount = xShardTxCount
        self.shardStats = shardStats


class AddMinorBlockHeaderResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32),
    ]

    def __init__(self, errorCode):
        self.errorCode = errorCode


# slave -> slave

class AddXshardTxListRequest(Serializable):
    FIELDS = [
        ("branch", Branch),
        ("minorBlockHash", hash256),
        ("txList", CrossShardTransactionList),
    ]

    def __init__(self, branch, minorBlockHash, txList):
        self.branch = branch
        self.minorBlockHash = minorBlockHash
        self.txList = txList


class AddXshardTxListResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32)
    ]

    def __init__(self, errorCode):
        self.errorCode = errorCode


class BatchAddXshardTxListRequest(Serializable):
    FIELDS = [
        ("addXshardTxListRequestList", PreprendedSizeListSerializer(4, AddXshardTxListRequest)),
    ]

    def __init__(self, addXshardTxListRequestList):
        self.addXshardTxListRequestList = addXshardTxListRequestList


class BatchAddXshardTxListResponse(Serializable):
    FIELDS = [
        ("errorCode", uint32)
    ]

    def __init__(self, errorCode):
        self.errorCode = errorCode


CLUSTER_OP_BASE = 128


class ClusterOp:

    # TODO: Remove cluster op base as cluster op should be independent to p2p op
    PING = 1 + CLUSTER_OP_BASE
    PONG = 2 + CLUSTER_OP_BASE
    CONNECT_TO_SLAVES_REQUEST = 3 + CLUSTER_OP_BASE
    CONNECT_TO_SLAVES_RESPONSE = 4 + CLUSTER_OP_BASE
    ADD_ROOT_BLOCK_REQUEST = 5 + CLUSTER_OP_BASE
    ADD_ROOT_BLOCK_RESPONSE = 6 + CLUSTER_OP_BASE
    GET_ECO_INFO_LIST_REQUEST = 7 + CLUSTER_OP_BASE
    GET_ECO_INFO_LIST_RESPONSE = 8 + CLUSTER_OP_BASE
    GET_NEXT_BLOCK_TO_MINE_REQUEST = 9 + CLUSTER_OP_BASE
    GET_NEXT_BLOCK_TO_MINE_RESPONSE = 10 + CLUSTER_OP_BASE
    GET_UNCONFIRMED_HEADERS_REQUEST = 11 + CLUSTER_OP_BASE
    GET_UNCONFIRMED_HEADERS_RESPONSE = 12 + CLUSTER_OP_BASE
    GET_ACCOUNT_DATA_REQUEST = 13 + CLUSTER_OP_BASE
    GET_ACCOUNT_DATA_RESPONSE = 14 + CLUSTER_OP_BASE
    ADD_TRANSACTION_REQUEST = 15 + CLUSTER_OP_BASE
    ADD_TRANSACTION_RESPONSE = 16 + CLUSTER_OP_BASE
    ADD_MINOR_BLOCK_HEADER_REQUEST = 17 + CLUSTER_OP_BASE
    ADD_MINOR_BLOCK_HEADER_RESPONSE = 18 + CLUSTER_OP_BASE
    ADD_XSHARD_TX_LIST_REQUEST = 19 + CLUSTER_OP_BASE
    ADD_XSHARD_TX_LIST_RESPONSE = 20 + CLUSTER_OP_BASE
    SYNC_MINOR_BLOCK_LIST_REQUEST = 21 + CLUSTER_OP_BASE
    SYNC_MINOR_BLOCK_LIST_RESPONSE = 22 + CLUSTER_OP_BASE
    ADD_MINOR_BLOCK_REQUEST = 23 + CLUSTER_OP_BASE
    ADD_MINOR_BLOCK_RESPONSE = 24 + CLUSTER_OP_BASE
    CREATE_CLUSTER_PEER_CONNECTION_REQUEST = 25 + CLUSTER_OP_BASE
    CREATE_CLUSTER_PEER_CONNECTION_RESPONSE = 26 + CLUSTER_OP_BASE
    DESTROY_CLUSTER_PEER_CONNECTION_COMMAND = 27 + CLUSTER_OP_BASE
    GET_MINOR_BLOCK_REQUEST = 29 + CLUSTER_OP_BASE
    GET_MINOR_BLOCK_RESPONSE = 30 + CLUSTER_OP_BASE
    GET_TRANSACTION_REQUEST = 31 + CLUSTER_OP_BASE
    GET_TRANSACTION_RESPONSE = 32 + CLUSTER_OP_BASE
    BATCH_ADD_XSHARD_TX_LIST_REQUEST = 33 + CLUSTER_OP_BASE
    BATCH_ADD_XSHARD_TX_LIST_RESPONSE = 34 + CLUSTER_OP_BASE
    EXECUTE_TRANSACTION_REQUEST = 35 + CLUSTER_OP_BASE
    EXECUTE_TRANSACTION_RESPONSE = 36 + CLUSTER_OP_BASE
    GET_TRANSACTION_RECEIPT_REQUEST = 37 + CLUSTER_OP_BASE
    GET_TRANSACTION_RECEIPT_RESPONSE = 38 + CLUSTER_OP_BASE


CLUSTER_OP_SERIALIZER_MAP = {
    ClusterOp.PING: Ping,
    ClusterOp.PONG: Pong,
    ClusterOp.CONNECT_TO_SLAVES_REQUEST: ConnectToSlavesRequest,
    ClusterOp.CONNECT_TO_SLAVES_RESPONSE: ConnectToSlavesResponse,
    ClusterOp.ADD_ROOT_BLOCK_REQUEST: AddRootBlockRequest,
    ClusterOp.ADD_ROOT_BLOCK_RESPONSE: AddRootBlockResponse,
    ClusterOp.GET_ECO_INFO_LIST_REQUEST: GetEcoInfoListRequest,
    ClusterOp.GET_ECO_INFO_LIST_RESPONSE: GetEcoInfoListResponse,
    ClusterOp.GET_NEXT_BLOCK_TO_MINE_REQUEST: GetNextBlockToMineRequest,
    ClusterOp.GET_NEXT_BLOCK_TO_MINE_RESPONSE: GetNextBlockToMineResponse,
    ClusterOp.ADD_MINOR_BLOCK_REQUEST: AddMinorBlockRequest,
    ClusterOp.ADD_MINOR_BLOCK_RESPONSE: AddMinorBlockResponse,
    ClusterOp.GET_UNCONFIRMED_HEADERS_REQUEST: GetUnconfirmedHeadersRequest,
    ClusterOp.GET_UNCONFIRMED_HEADERS_RESPONSE: GetUnconfirmedHeadersResponse,
    ClusterOp.ADD_MINOR_BLOCK_HEADER_REQUEST: AddMinorBlockHeaderRequest,
    ClusterOp.ADD_MINOR_BLOCK_HEADER_RESPONSE: AddMinorBlockHeaderResponse,
    ClusterOp.ADD_XSHARD_TX_LIST_REQUEST: AddXshardTxListRequest,
    ClusterOp.ADD_XSHARD_TX_LIST_RESPONSE: AddXshardTxListResponse,
    ClusterOp.GET_ACCOUNT_DATA_REQUEST: GetAccountDataRequest,
    ClusterOp.GET_ACCOUNT_DATA_RESPONSE: GetAccountDataResponse,
    ClusterOp.ADD_TRANSACTION_REQUEST: AddTransactionRequest,
    ClusterOp.ADD_TRANSACTION_RESPONSE: AddTransactionResponse,
    ClusterOp.SYNC_MINOR_BLOCK_LIST_REQUEST: SyncMinorBlockListRequest,
    ClusterOp.SYNC_MINOR_BLOCK_LIST_RESPONSE: SyncMinorBlockListResponse,
    ClusterOp.CREATE_CLUSTER_PEER_CONNECTION_REQUEST: CreateClusterPeerConnectionRequest,
    ClusterOp.CREATE_CLUSTER_PEER_CONNECTION_RESPONSE: CreateClusterPeerConnectionResponse,
    ClusterOp.DESTROY_CLUSTER_PEER_CONNECTION_COMMAND: DestroyClusterPeerConnectionCommand,
    ClusterOp.GET_MINOR_BLOCK_REQUEST: GetMinorBlockRequest,
    ClusterOp.GET_MINOR_BLOCK_RESPONSE: GetMinorBlockResponse,
    ClusterOp.GET_TRANSACTION_REQUEST: GetTransactionRequest,
    ClusterOp.GET_TRANSACTION_RESPONSE: GetTransactionResponse,
    ClusterOp.BATCH_ADD_XSHARD_TX_LIST_REQUEST: BatchAddXshardTxListRequest,
    ClusterOp.BATCH_ADD_XSHARD_TX_LIST_RESPONSE: BatchAddXshardTxListResponse,
    ClusterOp.EXECUTE_TRANSACTION_REQUEST: ExecuteTransactionRequest,
    ClusterOp.EXECUTE_TRANSACTION_RESPONSE: ExecuteTransactionResponse,
    ClusterOp.GET_TRANSACTION_RECEIPT_REQUEST: GetTransactionReceiptRequest,
    ClusterOp.GET_TRANSACTION_RECEIPT_RESPONSE: GetTransactionReceiptResponse,
}
